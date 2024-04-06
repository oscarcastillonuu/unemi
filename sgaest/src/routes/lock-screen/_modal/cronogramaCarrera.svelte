<script lang="ts">
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { Icon } from 'sveltestrap';
	export let aData;
	let aModalidad = {};
	//let aModalidades = [];
	let aCoordinaciones = [];
	const dispatch = createEventDispatcher();
	onMount(async () => {
		//	const _aModalidades = [...((await aData['aModalidades']) ?? [])];
		const _aCoordinaciones = [...((await aData['aCoordinaciones']) ?? [])];
		const _aModalidad = { ...((await aData['aModalidad']) ?? {}) };
		//console.log(aCoordinaciones);
		if ('name' in _aModalidad) {
			_aModalidad['name'] = _aModalidad['name'].toLowerCase();
		}
		aModalidad = { ..._aModalidad };
		//aModalidades = [..._aModalidades];
		aCoordinaciones = [..._aCoordinaciones];
	});
	onDestroy(() => {
		console.log(`Destroyed `);
		/*aModalidad = {};
		aModalidades = [];
		aCoordinaciones = [];*/
	});
	const cerrarModal = () => {
		dispatch('actionRun', { action: 'closeModal' });
	};
	const openModalidades = async () => {
		//onDestroy();
		dispatch('actionRun', {
			action: 'openModalidades'
		});
	};

	const openJornadas = async (aCoordinacion, aCarrera) => {
		//onDestroy();
		dispatch('actionRun', {
			action: 'openJornadas',
			aModalidad: aModalidad,
			aCoordinacion: aCoordinacion,
			aCarrera: aCarrera
		});
	};
</script>

<div class="px-4">
	<div class="d-lg-flex justify-content-between align-items-center">
		<div class="border-start border-5 border-warning px-2 rounded-start">
			<h3 class="m-0 p-0 fw-bold" style="color: #1c3247;">
				Carreras de la modalidad <span class="text-danger fw-bold"
					>{aModalidad ? aModalidad.name : ''}</span
				>
			</h3>
			<!--<p class="m-0 p-0" style="text-align: left; color: #264763; opacity: 1;">
						Recuerda que podrás elegir máximo {ePeriodo.num_career} carreras de tu preferencia.
					</p>-->
		</div>
		<div class="d-flex">
			<a
				href="javascript:void(0);"
				on:click={() => openModalidades()}
				class="btn btn-warning my-sm-2 btn-sm "
			>
				<spna class="">Ver otras modalidades</spna>
			</a>
		</div>
	</div>
	<div class="row">
		<div class="col-12">
			{#if aCoordinaciones.length > 0}
				<div
					class="row row-cols-1 row-cols-md-1 row-cols-sm-1 row-cols-xs-1 row-cols-lg-2 row-cols-xl-3 g-3 justify-content-center"
				>
					{#each aCoordinaciones as aCoordinacion}
						<div class="col">
							<div class="card border-0 shadow-none h-100">
								<div class="card-body ">
									<h6 class="card-title fw-bold text-center" style="color: #1c3247;">
										{aCoordinacion.name}
									</h6>
									<p class="text-center" style="color: #264763; opacity: 1;">
										{aCoordinacion.alias}
									</p>
									{#if aCoordinacion.aCarreras}
										{#each aCoordinacion.aCarreras as aCarrera}
											<div
												class="border-bottom py-1 d-flex justify-content-between align-items-center"
											>
												<div>
													<i class="fe fe-arrow-right me-2" />
													{aCarrera.name}
												</div>
												<button
													class="btn btn-secondary btn-sm rounded-pill"
													on:click={() => openJornadas(aCoordinacion, aCarrera)}>Ver</button
												>
											</div>
										{/each}
									{/if}
								</div>
							</div>
						</div>
					{/each}
				</div>
			{:else}
				<h3 class="text-secondary fw-bold text-center py-3">
					No existe carreras de la modalidad {aModalidad ? aModalidad.name : ''}
				</h3>
			{/if}
		</div>
		<!--{#if aModalidades}
			<div class="col-lg-3 col-md-3 col-12">
				<div class="me-xl-5 me-lg-3 me-sm-0 me-0">
					<div class="border-start border-5 border-warning px-2 rounded-start">
						<h4 class="m-0 p-0 fw-bold" style="color: #1c3247;">Otras Modalidades</h4>
					</div>
					<div class="mt-3">
						{#each aModalidades as aModalidad}
							<div class="card border border-secondary border-2 shadow-none card-dashed-hover p-2">
								<a
									href="javascript:void(0);"
									class="h-100 text-center"
									on:click={() => openCarreras(aModalidad)}
								>
									<div class="">
										<img src={aModalidad.imagen} alt="" class="icon-lg mb-3" />
										<h5 class="text-danger fw-bold">{aModalidad.name}</h5>
									</div>
								</a>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}-->
	</div>
</div>
