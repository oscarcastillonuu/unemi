<script lang="ts">
	import { Toast, ToastHeader, ToastBody } from 'sveltestrap';
	import { toasts } from '$lib/store/toastStore';
	import { onDestroy } from 'svelte';

	/*$: {
		if ($toasts.id !== undefined) {
			const Noty = { ...$toasts };
			Swal.fire(Noty);
		}
	}*/
	
	onDestroy(() => {
		clearInterval($toasts);
	});
</script>

{#if $toasts}
	<div
		class="toast-container position-fixed top-4 end-0"
		aria-live="polite"
		aria-atomic="true"
		style="z-index: 2090;"
	>
		{#each $toasts as toast}
			<div style="position: absolute; top: 0; right: 0; ">
				<Toast
					autohide={toast.autohide}
					isOpen={toast.isOpen}					
					class="m-2 m-t-100 {toast.bg} {toast.color}"
					role="status"
					aria-live="polite"
					aria-atomic="true"
					delay={toast.delay}
					
				>
					<ToastHeader class="{toast.bg} {toast.color}" icon={toast.icon} toggle={toast.toggle}>
						{toast.header}
					</ToastHeader>
					<ToastBody>
						{toast.body}
					</ToastBody>
				</Toast>
			</div>
		{/each}
	</div>
{/if}
