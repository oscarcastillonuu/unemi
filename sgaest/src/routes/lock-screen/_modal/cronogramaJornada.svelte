<script lang="ts">
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { Icon } from 'sveltestrap';
	export let aData;
	let aModalidad = {};
	let aCoordinacion = {};
	let aCarrera = {};
	let aJornadas = [];
	const dispatch = createEventDispatcher();
	onMount(async () => {
		//	const _aModalidades = [...((await aData['aModalidades']) ?? [])];
		const _aJornadas = [...((await aData['aJornadas']) ?? [])];
		const _aModalidad = { ...((await aData['aModalidad']) ?? {}) };
		const _aCoordinacion = { ...((await aData['aCoordinacion']) ?? {}) };
		const _aCarrera = { ...((await aData['aCarrera']) ?? {}) };
		//console.log(aJornadas);
		if ('name' in _aModalidad) {
			_aModalidad['name'] = _aModalidad['name'].toLowerCase();
		}
		if ('name' in _aCoordinacion) {
			_aCoordinacion['name'] = _aCoordinacion['name'].toLowerCase();
		}
		if ('name' in _aCarrera) {
			_aCarrera['name'] = _aCarrera['name'].toLowerCase();
		}
		aModalidad = { ..._aModalidad };
		aCoordinacion = { ..._aCoordinacion };
		aCarrera = { ..._aCarrera };
		aJornadas = [..._aJornadas];
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
	const openCarreras = async () => {
		//onDestroy();
		dispatch('actionRun', {
			action: 'openCarreras',
			aModalidad: aModalidad
		});
	};
</script>

<div class="px-4">
	<div class="d-lg-flex justify-content-between align-items-center">
		<div class="border-start border-5 border-warning px-2 rounded-start">
			<h4 class="m-0 p-0 fw-bold" style="color: #1c3247;">
				Jornadas de la carrera <span class="text-danger fw-bold"
					>{aCarrera ? aCarrera.name : ''}</span
				>
				de la modalidad <span class="text-danger fw-bold">{aModalidad ? aModalidad.name : ''}</span>
				de la <span class="text-danger fw-bold">{aCoordinacion ? aCoordinacion.name : ''}</span>
			</h4>
			<!--<p class="m-0 p-0" style="text-align: left; color: #264763; opacity: 1;">
						Recuerda que podrás elegir máximo {ePeriodo.num_career} carreras de tu preferencia.
					</p>-->
		</div>
		<div class="d-flex">
			<a
				href="javascript:void(0);"
				on:click={() => openCarreras()}
				class="btn btn-warning my-sm-2 btn-sm "
			>
				<spna class="">Ver otras carreras</spna>
			</a>
		</div>
	</div>
	<div class="row">
		<div class="col-12">
			{#if aJornadas.length > 0}
				<div
					class="row row-cols-1 row-cols-md-3 row-cols-sm-1 row-cols-xs-1 row-cols-lg-3 row-cols-xl-3 g-3 justify-content-center"
				>
					{#each aJornadas as aJornada}
						<div class="col">
							<div class="card border-0 shadow-none h-100">
								<img
									src={aJornada.imagen}
									alt=""
									class="rounded-top mx-auto"
									width="80px"
									height="80px"
								/>
								<div class="card-body ">
									<h5 class="card-title fw-bold text-center" style="color: #1c3247;">
										{aJornada.name}
									</h5>
									<!--{#if aJornada.aNiveles}
										<div class="d-flex align-items-center">
											<div class="avatar-group">
												{#each aJornada.aNiveles as aNivel}
													<span class="avatar avatar-sm">
														<div
															class="icon-shape icon-lg bg-light-primary text-primary rounded-circle imgtooltip "
															data-template={aNivel.id}
														>
															{aNivel.alias}
														</div>
														<span id={aNivel.id} class="d-none">
															<small class="fw-semibold">Paul Haney</small>
														</span>
													</span>
												{/each}
											</div>
										</div>
										
									{/if}-->

									<ul class="list-group list-group-flush mt-4">
										<li class="list-group-item p-0 pt-1 border-0">
											<div class="d-flex justify-content-between">
												<span class="fw-bold">Inicio</span>
												<div class="text-left">
													<p class="text-dark mb-0 fs-7">{aJornada.fecha_inicio}</p>
													<p class="text-dark mb-0 fs-7">{aJornada.hora_inicio}</p>
												</div>
											</div>
										</li>
										<li class="list-group-item p-0 pt-1">
											<div class="d-flex justify-content-between">
												<span class="fw-bold">Fin</span>
												<div class="text-left">
													<p class="text-dark mb-0 fs-7">{aJornada.fecha_fin}</p>
													<p class="text-dark mb-0 fs-7">{aJornada.hora_fin}</p>
												</div>
											</div>
										</li>
									</ul>
								</div>
								<div class="card-footer p-0 border-0">
									<!--<div class="d-flex justify-content-between">
										<div class="w-50 py-3 px-4">
											<h6 class="mb-0">Inicio:</h6>
											<p class="text-dark fs-6 fw-semibold mb-0">{aJornada.inicio}</p>
										</div>
										<div class="w-50 py-3 px-4">
											<h6 class="mb-0">Fin:</h6>
											<p class="text-dark fs-6 fw-semibold mb-0">$5,200</p>
										</div>
									</div>-->
								</div>
							</div>
							<!--<div class="card border-0 shadow-none h-100">
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
												<button class="btn btn-secondary btn-sm rounded-pill" on:click={() => {}}
													>Ver</button
												>
											</div>
										{/each}
									{/if}
								</div>
							</div>-->
						</div>
					{/each}
				</div>
			{:else}
				<h4 class="text-secondary fw-bold text-center py-3">
					No existe Jornadas de la carrera {aCarrera ? aCarrera.name : ''} de la modalidad {aModalidad
						? aModalidad.name
						: ''} de la facultad {aCoordinacion ? aCoordinacion.name : ''}
				</h4>
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
