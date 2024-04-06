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
	let ePerfilInscripcion = {};
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePerfilInscripcion = aData.ePerfilInscripcion ?? {};
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosDiscapacidad') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_3');
			menu.click();
		}
	};

	const openModalEdit = () => {
		modalDetalleContent = ComponentEdit;
		mOpenModal = !mOpenModal;
		// modalTitle = 'Actualizar datos personales';
		aDataModal = { ePerfilInscripcion: ePerfilInscripcion };
	};
</script>

{#if ePerfilInscripcion}
	<div class="card border-0 mx-xl-12 mx-lg-10 mx-md-0 mx-0">
		<div class="card-header d-lg-flex justify-content-between align-items-center">
			<div class="mb-3 mb-lg-0">
				<h3 class="mb-0">Discapacidad</h3>
				<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
			</div>
			<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>
		</div>
		<div class="card-body">
			<div class="pt-0 pb-5">
				<div class="row mb-4">
					<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
						<span class="d-block">
							<span class="h5">¿Tiene discapacidad?</span>
							{#if ePerfilInscripcion.tienediscapacidad}
								<span class="badge bg-success ms-2"> SI</span>
							{:else}
								<span class="badge bg-danger ms-2"> NO</span>
							{/if}
						</span>
						<!--<p class="mb-0 fs-6">Subscription ID: #100010002</p>-->
					</div>
					{#if ePerfilInscripcion.tienediscapacidad}
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Tipo</span>
							<h6 class="mb-0">{ePerfilInscripcion.tipodiscapacidad.nombre ?? 'S/N'}</h6>
						</div>

						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Nº Carnet</span>
							<h6 class="mb-0">{ePerfilInscripcion.carnetdiscapacidad ?? 'S/N'}</h6>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Porcentaje</span>
							<h6 class="mb-0">{ePerfilInscripcion.porcientodiscapacidad ?? '0'} %</h6>
						</div>

						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Institución valida</span>
							<h6 class="mb-0">{ePerfilInscripcion.institucionvalida.nombre ?? 'S/N'}</h6>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-2 mb-lg-4">
							<!-- Custom Switch -->
							<span class="fs-6">Documento/Archivo</span>
							{#if ePerfilInscripcion.download_archivo}
								<a
									class="btn btn-link text-primary m-0 p-0"
									href={ePerfilInscripcion.download_archivo}
									target="_blank">Ver archivo</a
								>
							{:else}
								<h6 class="mb-0">S/N</h6>
							{/if}
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
