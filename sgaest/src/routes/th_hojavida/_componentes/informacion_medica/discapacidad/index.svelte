<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import ComponentEdit from './edit.svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
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
		if (action == 'saveDatosPersonalesDiscapacidad') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_5');
			menu.click();
		}
	};

	const openModalEdit = () => {
		modalDetalleContent = ComponentEdit;
		mOpenModal = !mOpenModal;
		// modalTitle = 'Actualizar datos personales';
		aDataModal = { ePerfilInscripcion: ePerfilInscripcion };
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'md';
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

{#if ePerfilInscripcion}
	<div class="card">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Discapacidad</h3>
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
				<div class="col">
					<span class="d-block">
						<span class="fs-6">Tiene discapacidad:</span>
						<h6 class="mb-0">
							{#if ePerfilInscripcion.tienediscapacidad}
								SI
							{:else}
								NO
							{/if}
						</h6>
					</span>
					<!--<p class="mb-0 fs-6">Subscription ID: #100010002</p>-->
				</div>
				{#if ePerfilInscripcion.tienediscapacidad}
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Tipo:</span>
						<h6 class="mb-0">{ePerfilInscripcion.tipodiscapacidad.nombre ?? 'S/N'}</h6>
					</div>

					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Nº Carnet:</span>
						<h6 class="mb-0">{ePerfilInscripcion.carnetdiscapacidad ?? 'S/N'}</h6>
					</div>
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Porcentaje:</span>
						<h6 class="mb-0">{ePerfilInscripcion.porcientodiscapacidad ?? '0'} %</h6>
					</div>

					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Institución valida:</span>
						<h6 class="mb-0">{ePerfilInscripcion.institucionvalida.nombre ?? 'S/N'}</h6>
					</div>
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Carnet:</span>

						{#if ePerfilInscripcion.download_archivo}
							<a
								href="javascript:;"
								class=""
								on:click={() => view_pdf(ePerfilInscripcion.download_archivo)}
								id="Tooltip_raza"
							>
								<i class="bi bi-eye text-warning" />
							</a>

							<Tooltip target="Tooltip_raza" placement="top"
								>Visualizar archivo de Etnia/Pueblo</Tooltip
							>
							{#if ePerfilInscripcion.estadoarchivodiscapacidad_display === 'VALIDADO'}
								<span class="badge-dot bg-success" id="Tooltip_raza_estado">VALIDADO</span>
							{:else if ePerfilInscripcion.estadoarchivodiscapacidad_display === 'RECHAZADO'}
								<span class="badge-dot bg-danger" id="Tooltip_raza_estado">RECHAZADO</span>
							{:else}
								<span class="badge-dot bg-secondary" id="Tooltip_raza_estado">CARGADO</span>
							{/if}
							<Tooltip target="Tooltip_raza_estado" placement="top"
								>Estado de archivo: {ePerfilInscripcion.estadoarchivodiscapacidad_display ??
									'CARGADO'}</Tooltip
							>
						{:else}
							<h6 class="mb-0">S/N</h6>
						{/if}
					</div>
				{/if}
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
