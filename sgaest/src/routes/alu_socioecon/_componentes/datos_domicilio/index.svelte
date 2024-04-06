<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentEdit from './edit.svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let ePersona = {};
	let ePais;
	let eProvincia;
	let eCanton;
	let eParroquia;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePersona = aData.ePersona ?? {};
			if (ePersona.pais) {
				ePais = { ...ePersona.pais };
			}
			if (ePersona.provincia) {
				eProvincia = { ...ePersona.provincia };
			}
			if (ePersona.canton) {
				eCanton = { ...ePersona.canton };
			}
			if (ePersona.parroquia) {
				eParroquia = { ...ePersona.parroquia };
			}
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosDomicilio') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_5');
			menu.click();
		}
	};

	const openModalEdit = () => {
		modalDetalleContent = ComponentEdit;
		mOpenModal = !mOpenModal;
		aDataModal = { ePersona: ePersona };
	};
</script>

{#if ePersona}
	<div class="card border-0 mx-0">
		<div class="card-header d-lg-flex justify-content-between align-items-center">
			<div class="mb-3 mb-lg-0">
				<h3 class="mb-0">Datos de domicilio o residencia actual</h3>
			</div>
			<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>
		</div>
		<div class="card-body">
			<div class="pt-0 pb-5">
				<div class="row g-3">
					{#if ePais}
						<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Pais</span>
							<h6 class="mb-0">{ePais.nombre}</h6>
						</div>
					{/if}
					{#if eProvincia}
						<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Provincia</span>
							<h6 class="mb-0">{eProvincia.nombre}</h6>
						</div>
					{/if}
					{#if eCanton}
						<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Canton</span>
							<h6 class="mb-0">{eCanton.nombre}</h6>
						</div>
					{/if}
					{#if eParroquia}
						<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Parroquia</span>
							<h6 class="mb-0">{eParroquia.nombre}</h6>
						</div>
					{/if}
					<div class="col-lg-4 col-md-4 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Calle principal</span>
						<h6 class="mb-0">{ePersona.direccion}</h6>
					</div>

					<div class="col-lg-4 col-md-4 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Calle secundaria</span>
						<h6 class="mb-0">{ePersona.direccion2}</h6>
					</div>
					<div class="col-lg-4 col-md-4 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Número</span>
						<h6 class="mb-0">{ePersona.num_direccion}</h6>
					</div>

					<div class="col-lg-4 col-md-4 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Referencia</span>
						<h6 class="mb-0">{ePersona.referencia}</h6>
					</div>
					<div class="col-lg-4 col-md-4 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Teléfono domicilio</span>
						<h6 class="mb-0">{ePersona.telefono_conv}</h6>
					</div>
					<div class="col-lg-4 col-md-6 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Celular</span>
						<h6 class="mb-0">{ePersona.telefono}</h6>
					</div>
					<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Documento/Archivo croquis</span>
						{#if ePersona.download_croquis}
							<a
								class="btn btn-link text-primary m-0 p-0"
								href={ePersona.download_croquis}
								target="_blank">Ver archivo</a
							>
						{:else}
							<h6 class="mb-0">S/N</h6>
						{/if}
					</div>
					<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
						<!-- Custom Switch -->
						<span class="fs-6">Documento/Archivo planilla de luz</span>
						{#if ePersona.download_planilla_luz}
							<a
								class="btn btn-link text-primary m-0 p-0"
								href={ePersona.download_planilla_luz}
								target="_blank">Ver archivo</a
							>
						{:else}
							<h6 class="mb-0">S/N</h6>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
{/if}
