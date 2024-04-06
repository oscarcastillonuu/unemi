<script lang="ts">
	import { SvelteToast } from '@zerodevx/svelte-toast'; //https://github.com/zerodevx/svelte-toast
</script>

<SvelteToast />
<div class="wrap">
	<SvelteToast target="newNotificationToast" options={{ initial: 0, intro: { y: -64 } }} />
</div>
<style>
	.wrap {
	  --toastContainerTop: 0.5rem;
	  --toastContainerRight: 0.5rem;
	  --toastContainerBottom: auto;
	  --toastContainerLeft: 0.5rem;
	  --toastWidth: 100%;
	  --toastMinHeight: 2rem;
	  --toastPadding: 0 0.5rem;
	  font-size: 0.875rem;
	}
	@media (min-width: 40rem) {
	  .wrap {
		--toastContainerRight: auto;
		--toastContainerLeft: calc(50vw - 20rem);
		--toastWidth: 40rem;
	  }
	}
  </style>