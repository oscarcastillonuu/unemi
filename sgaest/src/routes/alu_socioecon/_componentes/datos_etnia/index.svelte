<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentEdit from './edit.svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import { Tooltip } from 'sveltestrap';
	let mOpenModal = false;
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let ePerfilInscripcion = undefined;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePerfilInscripcion = aData.ePerfilInscripcion ?? undefined;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosPersonalesEtnia') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_2');
			menu.click();
		}
	};

	const openModalEdit = () => {
		modalDetalleContent = ComponentEdit;
		mOpenModal = !mOpenModal;
		// modalTitle = 'Actualizar datos personales';
		aDataModal = { ePerfilInscripcion: ePerfilInscripcion };
	};
	const view_pdf = (url) => {
		aDataModal = { url: url };
		modalDetalleContent = ComponentViewPDF;
		mOpenModal = !mOpenModal;
		mTitleModal = 'Ver pdf';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};
</script>

{#if ePerfilInscripcion != undefined}
	<div class="card border-0">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Datos de étnia, pueblo y nacionalidades</h3>
				<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
			</div>
			<div>
				<button class="btn btn-success btn-sm btn-cian-opacity" on:click={() => openModalEdit()}
					><i class="fe fe-edit " /> Editar</button
				>
			</div>
		</div>

		<div class="card-body">
			<div class="row g-3 row-cols-2 row-cols-sm-3 row-cols-md-3 row-cols-lg-3">
				{#if ePerfilInscripcion.raza}
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Étnia</span>
						<h6 class="mb-0">{ePerfilInscripcion.raza.nombre ?? 'S/N'}</h6>
					</div>
					{#if ePerfilInscripcion.raza.pk == 1}
						{#if ePerfilInscripcion.nacionalidadindigena}
							<div class="col">
								<!-- Custom Switch -->
								<span class="fs-6">Nacionalidad Indígena</span>
								<h6 class="mb-0">{ePerfilInscripcion.nacionalidadindigena.nombre ?? 'S/N'}</h6>
							</div>
						{/if}
					{/if}
				{/if}

				<div class="col">
					<span class="fs-6">Documento/Archivo</span>

					{#if ePerfilInscripcion.download_archivoraza}
						<a
							href="javascript:;"
							class=""
							on:click={() => view_pdf(ePerfilInscripcion.download_archivoraza)}
							id="Tooltip_raza"
						>
							<i class="bi bi-eye text-warning" />
						</a>

						<Tooltip target="Tooltip_raza" placement="top"
							>Visualizar archivo de Etnia/Pueblo</Tooltip
						>
						{#if ePerfilInscripcion.estadoarchivoraza_display === 'VALIDADO'}
							<span class="badge-dot bg-success" id="Tooltip_raza_estado">VALIDADO</span>
						{:else if ePerfilInscripcion.estadoarchivoraza_display === 'RECHAZADO'}
							<span class="badge-dot bg-danger" id="Tooltip_raza_estado">RECHAZADO</span>
						{:else}
							<span class="badge-dot bg-secondary" id="Tooltip_raza_estado">CARGADO</span>
						{/if}
						<Tooltip target="Tooltip_raza_estado" placement="top"
							>Estado de archivo: {ePerfilInscripcion.estadoarchivoraza_display}</Tooltip
						>
					{:else}
						<h6 class="mb-0">S/N</h6>
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
		{mOpenModal}
		mToggle={mToggleModal}
		mTitle={mTitleModal}
		mClass={mClassModal}
		mSize={mSizeModal}
		on:actionRun={actionRun}
	/>
{/if}
