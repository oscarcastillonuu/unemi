<script>
	import { fade, slide } from 'svelte/transition';
	import { quintOut } from 'svelte/easing';
	import { createEventDispatcher, onMount } from 'svelte';
	import Star from './Star.svelte';

	// User rating states
	let rating = null;
	let hoverRating = null;

	// form interaction states
	let collectFeedback = false;
	let feedbackCompleted = false;

	// "$:" triggers when something in the line changes
	// When these variables reach true/false, they trigger these functions
	$: collectFeedback && addWatchListeners();
	$: !collectFeedback && feedbackFormClosed();

	const dispatch = createEventDispatcher();

	function feedbackFormClosed() {
		feedbackCompleted = false;
		removeWatchListeners();
	}

	function addWatchListeners() {
		document.addEventListener('keydown', userDismissFeedback);
		document.addEventListener('click', userClickedOutsideOfFeedback);
	}
	function removeWatchListeners() {
		document.removeEventListener('keydown', userDismissFeedback);
		document.removeEventListener('click', userClickedOutsideOfFeedback);
	}
	function userClickedOutsideOfFeedback(event) {
		const container = document.getElementById('feedbackContiner');
		if (!container.contains(event.target)) {
			collectFeedback = false;
		}
	}
	function userDismissFeedback(event) {
		switch (event.key) {
			case 'Escape':
				collectFeedback = false;
				break;
			default:
				return;
		}
	}

	// using curried function to initialize hover with id
	const handleHover = (id) => () => {
		hoverRating = id;
	};
	const handleRate = (id) => (event) => {
		if (collectFeedback && rating && rating.toString() === event.srcElement.dataset.starid) {
			collectFeedback = false;
			return;
		}
		rating = id;
		collectFeedback = true;
		dispatch('actionRun', { action: 'handleChangeRate', rating: rating });
	};

	const handleReset = (id) => (event) => {
		rating = id;
		collectFeedback = false;
		dispatch('actionRun', { action: 'handleChangeRate', rating: rating });
	};

	let stars = [
		{ id: 1, title: 'One Star' },
		{ id: 2, title: 'Two Stars' },
		{ id: 3, title: 'Three Stars' },
		{ id: 4, title: 'Four Stars' },
		{ id: 5, title: 'Five Stars' }
	];
</script>

<div class="feedback">
	<span
		id="feedbackContiner"
		class="feedbackContainer"
		class:feedbackContainerDisabled={feedbackCompleted}
	>
		<span class="starContainer">
			{#each stars as star (star.id)}
				<Star
					filled={hoverRating ? hoverRating >= star.id : rating >= star.id}
					starId={star.id}
					on:mouseover={handleHover(star.id)}
					on:mouseleave={() => (hoverRating = null)}
					on:click={handleRate(star.id)}
				/>
			{/each}
		</span>
		<br />
		<p class="secondaryAction">
			{#if rating !== null}
				Gracias por tu comentario - <a
					href="javascript:;"
					class="fw-bold text-primary"
					on:click={handleReset(null)}>restablecer</a
				>
			{/if}
		</p>
	</span>
</div>

<style>
	.feedback {
		position: relative;
	}

	.cancel {
		background: none;
		text-decoration: underline;
		border: none;
	}
	.starContainer {
		display: inline-block;
		transition: background 0.2s ease-out;
		border-radius: 8px;
		padding: 4px 6px 0;
	}
	.feedbackContainer:hover .starContainer {
		/*background: #efefef;*/
	}
	.secondaryAction {
		margin: 8px;
		font-size: 12px;
		display: inline-block;
	}
	.feedbackContainerDisabled {
		pointer-events: none;
	}
	:global(button) {
		cursor: pointer;
	}
</style>
