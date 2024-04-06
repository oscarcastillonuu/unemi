<script lang="ts">
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { apiPOST, browserGet } from '$lib/utils/requestUtils';
	import { createEventDispatcher, onMount, onDestroy } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { browser } from '$app/env';
	import Swal from 'sweetalert2';
	const DEBUG = import.meta.env.DEV;
	export let aData;
	export let mToggle;
	export let mOpenModal;
	export let mTitle;
	let eBloque = {};
	let map;
	let load = true;
	const dispatch = createEventDispatcher();
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		console.log(aData.eBloque);
		eBloque = (await aData.eBloque) ?? {};
		await delay(2000);
		load = false;
		if (browser && eBloque && eBloque.descripcion && (eBloque.latitud || eBloque.longitud)) {
			const leaflet = await import('leaflet');

			const map = await leaflet.map('map').setView([-2.149876251823762, -79.60316864321923], 18);

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
	});

	onDestroy(() => {});
</script>

<Modal
	isOpen={mOpenModal}
	toggle={mToggle}
	size="lg"
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
	backdrop="static"
>
	{#if mTitle}
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
	{/if}
	<ModalBody>
		{#if !load}
			{#if eBloque}
				<div class="py-lg-6 bg-dark pt-0 pb-0">
					<div class="container">
						<div class="row">
							<div class="offset-xl-1 col-xl-10 col-md-12 col-12">
								<div class="row text-center">
									<div class="col-md-12 px-md-16 mb-2 mt-1">
										<!--<span class="text-uppercase text-primary fw-semi-bold ls-md"
											>{eAula.nombre}</span
										>-->
										<h2 class="h1 fw-bold mt-3 text-white mb-2">{eBloque.descripcion}</h2>
										{#if eBloque.observacion}
											<p class="mb-0 text-white-50 fs-4">{eBloque.observacion}</p>
										{/if}
									</div>
								</div>
								<div class="row align-items-center">
									{#if eBloque.latitud || eBloque.longitud}
										<div class="col-12">
											<div id="map" />
										</div>
									{/if}
									{#if eBloque.foto}
										<div class="col-12">
											<div>
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
			<div class="row justify-content-center align-items-center p-5 m-0">
				<div class="col-auto text-center">
					<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
					<h3>Verificando la información, espere por favor...</h3>
				</div>
			</div>
		{/if}
	</ModalBody>

	<ModalFooter class="pb-3 mb-3 d-lg-flex justify-content-end align-items-center">
		<div class="d-flex">
			<Button color="warning" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
		</div>
	</ModalFooter>
</Modal>

<!--{#if !isLoad}
	{#if eClase && eBloque}
		<div class="py-lg-6 bg-dark pt-0 pb-0">
			<div class="container">
				<div class="row">
					<div class="offset-xl-1 col-xl-10 col-md-12 col-12">
						<div class="row text-center">
							<div class="col-md-12 px-md-16 mb-2 mt-1">
								<span class="text-uppercase text-primary fw-semi-bold ls-md">{eAula.nombre}</span>
									<h2 class="h1 fw-bold mt-3 text-white mb-2">{eBloque.descripcion}</h2>
									{#if eBloque.observacion}
										<p class="mb-0 text-white-50 fs-4">{eBloque.observacion}</p>
									{/if}								
							</div>
						</div>
						<div class="row align-items-center">
							{#if eBloque.latitud || eBloque.longitud}
								<div class="col-12">
									<div id="map" />
								</div>
							{/if}
							{#if eBloque.foto}
								<div class="col-12">
									<div>
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
-->
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
