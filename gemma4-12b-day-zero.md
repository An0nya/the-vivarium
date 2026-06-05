<!--
DRAFT — Gemma-4-12B day-zero probing writeup. Geometry/probing bucket, first specimen.
Voice: first-person reactive, day-zero freshness. NOT the formal lab voice.
Figures: linked by source path + a note on what to crop/show. Source PNGs live in
~/Projects/rys-tools/scans/data/ — copy/convert into figures/ (SVG conversion + final
edit outsourced to a cheaper session). Each figure block says what part matters.
Methods (MLX hooks etc.) are deliberately NOT explained here — they point to methods.
-->
 
# I probed Gemma-4-12B's internals the day it dropped
 
Gemma 4 12B came out this afternoon. By the time the base model's full weights had landed on my drive for surgical experimentation (link to gemma31rys), I already had hidden-state scans running against an mlx quant. That's the whole pitch for this one: the methodology is fast enough that you can crack open a brand-new model the same day it ships and watch it think before anyone's had time to write the first fine-tune.
 
So that's what this is, a zero-day look inside a 48-layer dense model, while it still has the plastic film on.
 
I went in with open curiosity after a primer on how transformer models function, starting with the multilingual cosine scan we usually try to establish where in the model the language is transformed into meaning and back. After seeing a similar graph to Gemma4 31b, for no particular reason I wondered how much similarity two sentences with different words but ostensibly the same meaning would display in the model. That stray thought spiraled into a whole series of probes that showed me how transformer LLMs *work* and others that surprised me by upending my preconceptions.
 
---
 
## The one finding
 
Six probes, six <!--let's revisit and see exactly how many sets of probes and how many in each, it was more than 6-->totally different setups — paraphrases, minimal pairs, word senses, long-range callbacks, twelve languages, garden-path sleepers. Every single one of them lights up the **same band of layers, roughly L18 through L27.**
 
That band is where this model *"does meaning"*. Everything below it is still mostly working with initial surface form — tokens, spelling, word identity. Everything above it is already pivoting toward "what word comes next." The semantic understanding — the part where "the meaning" actually exists as a thing the model has computed — lives in that middle third.
 
I didn't design six probes to find one zone. I designed six probes to ask six different questions and the zone fell out of all of them. That convergence is the actual result here; the individual demos below are just the six camera angles.
 
> **Figure — the concept zone.** Source: `rys-tools/scans/data/gemma4_12b_mxfp4_centered_last.png` (+ `..._delta.png`). The centered-cosine layer scan. **Crop/annotate to highlight the L18–27 plateau.** This is the establishing shot — show it big, early. The delta plot (per-layer change) makes the "work happens in the middle" point even more bluntly; the front and back of the stack are quiet, the middle is where the residual stream is being rewritten.
 
---
 
## A detour through dead ends and one surprisingly good idea
 
Both the right instrument and the right probes took some finding. Here's how it actually went, because the wrong turns are half the story.
 
**The readout problem.** The first batch of probes I ran were paraphrase invariance and sensitivity tests — same meaning, different words, versus near-identical surface, flipped meaning. Standard last-token cosine similarity. The sensitivity probes came back looking flat. "The dog chased the cat" versus "the cat chased the dog" barely moved the summary number. My first instinct: aggregate over more tokens, try mean-pooling instead.
 
Mean-pooling made it worse. The reason, once I saw it, was obvious: mean-pooling is *permutation-invariant by construction*. "Dog chased cat" and "cat chased dog" are the same multiset of tokens — averaging throws away the word order that distinguishes them, so their pooled vectors are nearly identical no matter what attention did. I'd grabbed exactly the wrong tool for the one probe I was trying to fix.
 
Both approaches had the same blind spot: collapsing the whole sequence to one number loses *where* in the sentence meaning diverges. The signal was in the data; I just couldn't see it.
 
That's when the obvious question finally surfaced: can we just show all of it? Every token position, every layer, similarity as color? It tripped me up at first, as displaying four axes of data is difficult to do in a comprehensible way, but that actually revealed a cleaner readout option - per sentence pair it collapses cleanly to 2D: layer on one axis, token position on the other, cosine as the color. One heatmap per pair. Stack them and you can read "which token, which layer" without guessing in advance.
 
The one real gotcha is alignment: sentence pairs often differ in length, and an inserted word shifts every token after it. Naive position-vs-position would compare misaligned tokens and fabricate divergence. The fix was to sequence-align the two sentences first and only compare matched positions. No anchor guessing. The divergence just lights up wherever it lives.
 
That instrument is what made everything else visible.
 
**The homograph problem.** Now I needed good pairs to put through it. I started by asking for homophones — words that *sound* the same — and got corrected immediately. Homographs is what I wanted: words *spelled* the same with different meanings. Swapping "two" for "too" is instantly picked up as a meaningful difference just on the surface as they're different tokens, but homographs like "bank" derive their meaning from the surrounding context. The idea was - how similar can I make two sentences read from a letter to letter perspective while driving a wedge between the meanings of the two sentences visible enough to show up.
 
I spent a solid twenty minutes trying to write good ones, and most of them went the opposite direction: too many differences, too much ambiguity in the meaning. The problem is harder than it sounds: I needed a sentence where one early word completely changes the meaning of a *later unchanged* word, actual semantic recoloring <!--is this word salad, real etymology/linguistics, or flair that sounds dressed up like a student padding their essay?-->, not just two different sentences that happen to share a token. Half my attempts just swapped the subject and measured "these are two different sentences," which proves nothing. I kept reaching for clever garden-path constructions and they kept collapsing into red herrings.
 
The thing I was circling and couldn't name: I wanted an **inflection point**, a later token whose meaning is set by something earlier, so that even though it's byte-for-byte identical between two versions, it becomes the place where the geometry diverges. Not a changed token. A changed *reading* of an unchanged token.
 
Two probes finally cracked it. One was almost stupidly simple: "how do you do" (a greeting) versus "how do you do *it*" (an actual question). That one trailing word retroactively flips the whole phrase from ritual to inquiry, and the divergence shows up *upstream* of the word that caused it. The other was the crane probe. The moment those two worked, the frame clicked into place: find a shared token whose sense is set by something else in the sentence, and watch the layer where the model snaps to one meaning or another.
 
Everything below is downstream of that click.
 
## The crane that knew it was a bird
 
Take two sentences that are identical except for one early word:
 
- "At the **harbor**, we finally watched the crane today."
- "At the **marsh**, we finally watched the crane today."
The word "crane" is byte-for-byte the same token in both. A construction crane at the harbor, a bird at the marsh — but the model reads the exact same characters. So: when does the model's internal representation of "crane" *split* between the two readings?
 
Not at the input. At the input, "crane" is "crane" — the vectors are identical. The split happens **mid-stack**, layers deep, well after the word has been read. The model finishes reading "crane," carries it forward unchanged for several layers, and *then* — somewhere in the concept zone — decides which crane it is.
 
You can watch the moment it decides. The identical token diverges between the two sentences not where it enters, but where the model *commits*. Commitment lags the cue.
 
> **Figure — the sleeper heatmap.** Source: `rys-tools/scans/data/gemma4_12b_sleeper_heatmaps.png`. Per-token × per-layer divergence, two near-identical sentences aligned with difflib. **The part that matters: the "crane" column.** Show that it stays cold (identical) through the early layers and only heats up in the mid-stack rows. The companion `..._sleeper_lasttoken.png` is the line-graph version if a simpler figure is wanted. Caption should land the line: *the model knows "crane" is a bird before it finishes the sentence — and you can see the layer where it decides.*
 
It even survives distance. Push "harbor"/"marsh" and "crane" over a thousand tokens apart — further than the model's sliding-attention window — and the split still happens. The early word still recolors the later one. (More on *how* that's possible in the next one.)
 
> **Figure — distance-invariance, optional.** Source: `rys-tools/scans/data/gemma4_12b_distance_heatmaps.png`. Same demo, X and callback separated by 1000+ tokens. Only include if there's room; it's a robustness check on the crane finding, not a new point.
 
---
 
## Two different things called "understanding"
 
The distance result above forced a distinction I hadn't been careful about.
 
There are two separate things going on when a model "understands" a far-apart connection, and Gemma gates them **independently**:
 
1. **Access** — can the later token even *reach* the earlier one? That's an attention-architecture question. Gemma 4 alternates sliding-window attention (local, cheap) with global full-attention layers (can see the whole sequence). Past ~1024 tokens, only the global layers can bridge the gap.
2. **Computation** — once it has access, *where* does it actually compute the meaning? That's a depth question, and the answer is the concept zone, ~L17 onward.
These are not the same axis. I expected the long-range version to show divergence "turning on" at the first global attention layer — i.e. access-gated, early. It doesn't. The onset is still depth-gated, in the mid-stack, regardless of where the global layers sit. Access is necessary but it's not where the understanding *happens*. You need both gates open, and they're controlled by different knobs.
 
> **Figure — the staircase.** Source: `rys-tools/scans/data/gemma4_12b_staircase.png`. Short-range vs long-range (1112-token) callback, cosine at the shared token per layer, with the global-attention layers (5,11,17,23,29,35,41,47) marked as vertical lines. **What to show:** the long-range curve stays high (near 1.0) far longer and the divergence onset still lands in the mid-stack, not at the first global line. The marked global layers are the architecture made visible. Caption: *access and computation are different gates.*
 
---

## <!--other probe visualizer (toggle-able heat maps) plus interpretations-->

---
 
## What survives translation
 
Different question, same machine. Take one sentence, translate it into twelve languages across seven writing systems, and ask: at each layer, how close together do all twelve land? High convergence = the model has thrown away the language and kept the meaning.
 
Then do it for four *kinds* of sentence and compare:
 
- A concrete fact: "The sun rises in the east."
- An arithmetic fact: "Two plus three equals five."
- An emotional one: "She cried because she was sad."
- An abstract one: "Freedom is more important than money."
I'd have bet on concrete and numeric converging hardest — they feel the most universal, the most language-independent. Two plus three is five in every language, right?
 
Backwards. The order is **abstract > emotion > concrete > numeric.** The *abstract*, relational, propositional sentences are the most language-invariant. Arithmetic is the most language-*locked* — it stays tied to its surface symbols the longest and converges the least. <!--I'm not 100% sure of this explanation, let's tone down the confident-->
 
Which, once it's in front of you, makes sense: "freedom matters more than money" is a relationship between concepts, and the relationship is what's left after you strip the words. "Two plus three" is a string of number-symbols, and the model keeps holding onto the symbols. The meaning that crosses languages is the *relational* meaning, not the concrete one. Math is the least universal language in the building.
 
> **Figure — cross-lingual convergence by type.** Source: `rys-tools/scans/data/gemma4_12b_crosslang.png`. Four curves (one per sentence type), mean cosine over all 66 language-pairs per layer. **⚠️ This is the colorblind-critical figure** — four colored lines. It already uses distinct markers + linestyles per type (don't drop them in the SVG conversion); keep it cividis/viridis-safe. **What to show:** abstract on top, numeric on the bottom, and the spread opening up through the concept zone. Caption: *the meaning that survives translation is relational, not concrete.*
 
---
 
## Same word, two senses
 
One more angle, the most direct one. The WiC task (Words-in-Context) gives you pairs of sentences using the same word in either the same sense or different senses — "river *bank*" vs "savings *bank*." I tracked the target word's representation and asked where same-sense and different-sense pairs separate the most.
 
Peak separation: **L20.** Right in the middle of the zone. Word-sense disambiguation isn't an input-level lookup and it isn't a late decision — it's computed in the same band as everything else.
 
> **Figure — WiC sense bands.** Source: `rys-tools/scans/data/gemma4_12b_wic_bands.png`. Same-sense vs different-sense cosine bands across layers. **What to show:** the two bands are together early, fan apart through the mid-stack, peak gap at L20. Reinforces the zone from yet another dataset — good as a confirmation figure, doesn't need to be large.
 
<!--blurb crediting the WiC source and explaining it's research purpose? And maybe more context for this?-->

---

## <!--potential section?-->THE DIVERGENCE VIEWER
When does a word split?

The viewer below shows the per-layer cosine curve at the key token for eleven homograph probe pairs — sentences designed so the same word carries different meanings depending on context. Tokens shown in red are the divergent ones between the two readings. The shaded band marks the L17–27 concept zone.

The howdoyou probe <“How do you do it?” he asked the jogger> is the one where a trailing word retroactively flips the whole phrase from ritual greeting to genuine question. The divergence shows up upstream of the word that caused it.

>**Figure: todo - find some good examples of key tokens in a probe sample pair that show clean separation, without a bunch of noise. Actually maybe we can include the noisy ones too, as well as a control, but flag them as counterexamples or weak demonstrations. Illustrate which token the map is of. Or maybe we nix this and add just the heatmaps

---
 
## And then it throws it all away
 
The last thing worth pointing at: the very top of the stack.
 
After the model has done all this — built the meaning, disambiguated the senses, stripped the language — the final layer **collapses** a lot of it. The representations that were rich and semantic in the concept zone get reshaped at L47 into something else. That something else is "what token comes next." The last layer isn't holding the meaning; it's spending the meaning, converting understanding into a prediction and discarding the rest.
 
It's a clean reminder that the model's job isn't to understand the sentence. Understanding is a *means*. The concept zone is where the understanding lives, and the top of the stack is where it gets cashed out for the only thing the model is actually optimized to produce: the next word.
 
> **Figure — reuse the establishing scan.** The L47 drop is already visible in `gemma4_12b_mxfp4_centered_last.png` / `..._delta.png` from the top. Rather than a new figure, annotate the collapse on the establishing shot, or call back to it.
 
---
 
## What this is
 
This is the first entry in a probing notebook. The plan is to run this same battery — sleeper tokens, the two-gate staircase, cross-lingual convergence, WiC, paraphrase invariance — across other models, and see which findings are Gemma-specific and which are just *how transformers work.* Does every model put word-sense at ~40% of its depth? Is the boundary between language/tokens and meaning a single layer or does it gradually transform from one to the other? Is numeric always the most language-locked? Does everything collapse at the final layer? I don't know yet. That's the next several entries.
 
The methodology — how you actually pull per-layer hidden states out of a running MLX model, the hooks, the cosine math, the token alignment — is over in [methods](./methods.md), deliberately kept out of the way here.
 
For now: a brand-new 12-billion-parameter model, opened up on its launch day, and a middle third of its layers quietly doing all the thinking.
 
<!--
TODO before publish:
- copy/convert the 6 source PNGs into figures/ (SVG preferred; preserve markers+linestyles
  on the crosslang figure — it's the CB hazard). Outsource edit to cheaper session.
- methods.md link target doesn't exist yet in this repo — either stub it or point at the
  shared methods page once the root/hub exists.
- repo: this is its own repo+site; root hub links it alongside surgery + duologue.
- decide title/slug; "day-zero" framing has a shelf life — fine, that's the point.
-->