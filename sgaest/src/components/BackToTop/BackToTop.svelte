<script>
	import { Button, Icon, Tooltip } from 'sveltestrap';
	export let showOnPx = 150;
	let hidden = true;

	function goTop() {
		document.body.scrollIntoView();
	}

	function scrollContainer() {
		return document.documentElement || document.body;
	}

	function handleOnScroll() {
		if (!scrollContainer()) {
			return;
		}

		if (scrollContainer().scrollTop > showOnPx) {
			hidden = false;
		} else {
			hidden = true;
		}
	}
</script>

<svelte:window on:scroll={handleOnScroll} />

<div class="back-to-top" class:hidden>
	<Button color="primary" on:click={goTop} size="sm" id="Tooltip_back_to_top"
		><Icon name="arrow-up-circle-fill" /></Button
	>
	<Tooltip target="Tooltip_back_to_top" placement="left">Subir</Tooltip>
</div>

<style>
	.back-to-top {
		opacity: 1;
		font-size: 16px;
		transition: opacity 0.5s, visibility 0.5s;
		position: fixed;
		z-index: 99;
		right: 20px;
		user-select: none;
		bottom: 60px;
		/*color: white;
	  background-color: black;*/
	}

	.back-to-top:hover {
		box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
		transform: translateY(-7px);
	}

	.back-to-top.hidden {
		opacity: 0;
		visibility: hidden;
	}
	@media only screen and (max-width: 600px) {
		.back-to-top {
			font-size: 14px;
			bottom: 60px;
			right: 20px;
		}
		.back-to-top:hover {
			box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
			transform: translateY(-7px);
		}
		@media only screen and (max-width: 360px) {
			.back-to-top {
				font-size: 14px;
				bottom: 60px;
				right: 20px;
			}
			.back-to-top:hover {
				box-shadow: 0px 15px 20px rgba(0, 0, 0, 0.3);
				transform: translateY(-7px);
			}
		}
	}
</style>
