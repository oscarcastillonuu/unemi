<script lang="ts">
	import { onMount } from 'svelte';

	import { createEventDispatcher, onDestroy } from 'svelte';

	const dispatch = createEventDispatcher();

	export let aData;
	let eProducto;

	onMount(async () => {
		if (aData.eProducto) {
			eProducto = aData.eProducto;
		}
	});
</script>

{#if eProducto}
	<div class="card" style="">
		<div class="row g-0">
			<div class="col-md-4">
				<img src={eProducto.imagen} class="img-fluid rounded-start h-100" alt="" />
			</div>
			<div class="col-md-8">
				<div class="card-body">
					<h5 class="card-title">{eProducto.name}</h5>
					<p class="card-text">
						{eProducto.detail}
					</p>
					{#if eProducto.validity}
						<p class="card-text text-muted text-center">
							Tiempo de validez:
							<!--{eCertificado.validity_display}-->
							{#if eProducto.validity.type === 0}
								<span class="badge bg-badge">No aplica</span>
							{:else if eProducto.validity.type == 1}
								<span class="badge bg-danger">{eProducto.validity.display}</span>
							{:else if eProducto.validity.type == 2}
								<span class="badge bg-warning text-dark">{eProducto.validity.display}</span>
							{:else if eProducto.validity.type == 3}
								<span class="badge bg-success">{eProducto.validity.display}</span>
							{:else if eProducto.validity.time > 1}
								<span class="badge bg-info text-dark">{eProducto.validity.display}</span>
							{:else}
								<span class="badge bg-info text-dark">{eProducto.validity.display}</span>
							{/if}
						</p>
					{/if}
					{#if eProducto.cost > 0}
						<p class="card-text"><small class="text-muted">Costo: $ {eProducto.cost}</small></p>
					{:else}
						<p class="card-text"><small class="text-muted">No aplica costo</small></p>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
