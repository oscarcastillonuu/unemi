<script lang="ts">
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { Icon } from 'sveltestrap';
	export let aData;
	let aModalidades = [];
	const dispatch = createEventDispatcher();
	onMount(async () => {
		aModalidades = aData['aModalidades'] ?? [];
	});
	const cerrarModal = () => {
		dispatch('actionRun', { action: 'closeModal' });
	};
	const openCarreras = (aModalidad) => {
		dispatch('actionRun', {
			action: 'openCarreras',
			aModalidad: aModalidad
		});
	};
</script>

{#if aModalidades.length > 0}
	<div
		class="row row-cols-1 row-cols-md-1 row-cols-sm-1 row-cols-xs-1 row-cols-lg-3 row-cols-xl-3 g-2 justify-content-center mx-10"
	>
		{#each aModalidades as aModalidad}
			<div class="col">
				<div class="card border border-secondary border-2 card-dashed-hover p-2">
					<a
						href="javascript:void(0);"
						class="h-100 text-center"
						on:click={() => openCarreras(aModalidad)}
					>
						<!-- card body  -->
						<div class="">
							<img src={aModalidad.imagen} alt="" class="icon-xxl mb-3" />
							<h5 class="text-secondary fw-bold">{aModalidad.name}</h5>
						</div>
					</a>
				</div>
			</div>
		{/each}
	</div>
	<!--<ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
		{#each aModalidades as aModalidad}
			<li class="nav-item">
				<a
					class="nav-link"
					id="{aModalidad.alias}-tab"
					data-bs-toggle="pill"
					href="#{aModalidad.alias}"
					role="tab"
					aria-controls={aModalidad.alias}
					aria-selected="true"
					>{aModalidad.name}
				</a>
			</li>
		{/each}
	</ul>

	<div class="tab-content" id="pills-tabContent">
		{#each aModalidades as aModalidad}
			<div
				class="tab-pane fade show active"
				id={aModalidad.alias}
				role="tabpanel"
				aria-labelledby="{aModalidad.alias}-tab"
			>
				{aModalidad.aCoordinaciones}
			</div>
		{/each}
	</div>-->
{/if}
