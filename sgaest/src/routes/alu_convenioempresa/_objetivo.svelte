<script lang="ts">
	import { onMount } from 'svelte';

	export let aData;
	let objetivo = [];
	
	console.log(aData + 'aDATA');
	onMount(async () => {
		objetivo = aData.detalleobjetivo;		
	});
</script>

<div class="card-body">

    {#each objetivo as obj }
        {obj.objetivo}        
    {/each}

</div>