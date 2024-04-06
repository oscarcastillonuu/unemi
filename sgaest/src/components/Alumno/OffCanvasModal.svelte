<script lang="ts">
    import { createEventDispatcher } from 'svelte';
	import { Button, Offcanvas } from 'sveltestrap';
    import { loading } from '$lib/store/loadingStore';
    export let mToggle;
    export let mOpen = false;
    export let OffCanvasContent;
    export let aData;
    export let modalTitle;
    export let placement;

    const dispatch = createEventDispatcher();
	function actionRun(event) {
        loading.setLoading(true, 'Cargando, espere por favor...');
		dispatch('actionRun', event.detail);
	}
</script>

<Offcanvas 
header="{modalTitle}"
isOpen={mOpen}
toggle={mToggle}
backdrop={true}
placement={placement}
>
<svelte:component this={OffCanvasContent} {aData} on:actionRun={actionRun} />

</Offcanvas>
