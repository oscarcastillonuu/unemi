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
			if (ePersona.paisnacimiento) {
				ePais = { ...ePersona.paisnacimiento };
			}
			if (ePersona.provincianacimiento) {
				eProvincia = { ...ePersona.provincianacimiento };
			}
			if (ePersona.cantonnacimiento) {
				eCanton = { ...ePersona.cantonnacimiento };
			}
			if (ePersona.parroquianacimiento) {
				eParroquia = { ...ePersona.parroquianacimiento };
			}
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosNacimiento') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_4');
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
	<div class="card border-0 mx-xl-12 mx-lg-10 mx-md-0 mx-0">
		<div class="card-header d-lg-flex justify-content-between align-items-center">
			<div class="mb-3 mb-lg-0">
				<h3 class="mb-0">Datos de nacimiento</h3>
			</div>
			<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>
		</div>
		<div class="card-body">
			<div class="pt-0 pb-5">
				<div class="row g-3">
					{#if ePais}
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Pais</span>
							<h6 class="mb-0">{ePais.nombre}</h6>
						</div>
					{/if}
					{#if eProvincia}
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Provincia</span>
							<h6 class="mb-0">{eProvincia.nombre}</h6>
						</div>
					{/if}
					{#if eCanton}
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Canton</span>
							<h6 class="mb-0">{eCanton.nombre}</h6>
						</div>
					{/if}
					{#if eParroquia}
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Parroquia</span>
							<h6 class="mb-0">{eParroquia.nombre}</h6>
						</div>
					{/if}
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
