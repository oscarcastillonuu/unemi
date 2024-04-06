<script lang="ts">
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { apiPOST, browserGet } from '$lib/utils/requestUtils';
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { Spinner } from 'sveltestrap';
	import { browser } from '$app/env';
	import Swal from 'sweetalert2';
	const DEBUG = import.meta.env.DEV;
	export let aData;
	let isLoad = true;
	let eClase = {};
	let eAula = {};
	let eBloque = {};
	let map;

	const dispatch = createEventDispatcher();

	onMount(async () => {
		//console.log(aData.clase_id);

		const clase_id = aData.clase_id;
		if (clase_id) {
			const ds = browserGet('dataSession');
			if (ds != null || ds != undefined) {
				//const dataSession = JSON.parse(ds);
				const [res, errors] = await apiPOST(fetch, 'alumno/horario', {
					action: 'seeClassroomLocation',
					idc: clase_id
				});
				if (errors.length > 0) {
					addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
					dispatch('actionRun', { action: 'closeModal' });
					return {
						status: 302,
						redirect: '/'
					};
				} else {
					eClase = res.data.eClase;
					eAula = eClase.aula;
					eBloque = eAula.bloque;
					isLoad = false;
					if (browser && eBloque && eBloque.descripcion && (eBloque.latitud || eBloque.longitud)) {
						const leaflet = await import('leaflet');

						const map = leaflet.map('map').setView([-2.149876251823762, -79.60316864321923], 18);

						leaflet
							.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
								attribution: '© <a href="https://www.unemi.edu.ec">UNEMI</a>'
							})
							.addTo(map);

						leaflet
							.marker([eBloque.latitud, eBloque.longitud])
							.addTo(map)
							.bindPopup(`UNEMI<br>${eBloque.descripcion}`)
							.openPopup();
					}
				}
			}
		}
	});

	onDestroy(() => {});
</script>

{#if !isLoad}
	{#if eClase && eBloque}
		<div class="py-lg-6 bg-dark pt-0 pb-0">
			<div class="container">
				<div class="row">
					<div class="offset-xl-1 col-xl-10 col-md-12 col-12">
						<div class="row text-center">
							<!-- col -->
							<div class="col-md-12 px-md-16 mb-2 mt-1">
								<span class="text-uppercase text-primary fw-semi-bold ls-md">{eAula.nombre}</span>
								<!-- heading -->							
									<h2 class="h1 fw-bold mt-3 text-white mb-2">{eBloque.descripcion}</h2>
									<!-- text -->
									{#if eBloque.observacion}
										<p class="mb-0 text-white-50 fs-4">{eBloque.observacion}</p>
									{/if}								
							</div>
						</div>
						<div class="row align-items-center">
							{#if eBloque.latitud || eBloque.longitud}
								<!-- col -->
								<div class="col-12">
									<div id="map" />
								</div>
							{/if}
							{#if eBloque.foto}
								<div class="col-12">
									<div>
										<!-- Img -->
										<img
											src={eBloque.foto}
											onerror="this.onerror=null;this.src='./image.png'"
											class="img-fluid rounded-3 w-100"
										/>
									</div>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
		</div>
		{:else}
		<div class="row">
			<div class="col-12 text-center">
				<h2>NO EXISTE DATOS DEL BLOQUE</h2>
			</div>
		</div>
	{/if}
{:else}
	<div class="col-auto text-center">
		<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
		<h3>Verificando la información, espere por favor...</h3>
	</div>
{/if}

<style>
	@import 'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css';
	#map {
		height: 500px;
	}
	.map :global(.marker-text) {
		width: 100%;
		text-align: center;
		font-weight: 600;
		background-color: #444;
		color: #eee;
		border-radius: 0.5rem;
	}

	.map :global(.map-marker) {
		width: 30px;
		transform: translateX(-50%) translateY(-25%);
	}
</style>
