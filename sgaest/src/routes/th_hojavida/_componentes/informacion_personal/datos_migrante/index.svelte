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
	let eMigrantePersona = undefined;
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eMigrantePersona = aData.eMigrantePersona ?? undefined;
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosPersonalesMigrante') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_3');
			menu.click();
		}
	};

	const openModalEdit = () => {
		modalDetalleContent = ComponentEdit;
		mOpenModal = !mOpenModal;
		// modalTitle = 'Actualizar datos personales';
		aDataModal = { eMigrantePersona: eMigrantePersona };
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

{#if eMigrantePersona != undefined}
	<div class="card border-0">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Datos de direccion domiciliaria en el extranjero</h3>
				<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
			</div>
			{#if !eMigrantePersona.verificado}
				<div>
					<button class="btn btn-success btn-sm btn-cian-opacity" on:click={() => openModalEdit()}
						><i class="fe fe-edit " /> Editar</button
					>
				</div>
			{/if}
		</div>

		<div class="card-body">
			<div class="row g-3 row-cols-2 row-cols-sm-3 row-cols-md-2 row-cols-lg-5">
				<div class="col">
					<!-- Custom Switch -->
					<span class="fs-6">Migrante retornado:</span>
					<h6 class="mb-0">
						{#if eMigrantePersona.persona}
							SI
						{:else}
							NO
						{/if}
					</h6>
				</div>
				{#if eMigrantePersona.persona}
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">País residencia:</span>
						<h6 class="mb-0">
							{#if eMigrantePersona.paisresidencia}
								{eMigrantePersona.paisresidencia.nombre}
							{:else}
								S/P
							{/if}
						</h6>
					</div>
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Tiempo de residencia:</span>
						<h6 class="mb-0">
							{#if eMigrantePersona.anioresidencia || eMigrantePersona.mesresidencia}
								{eMigrantePersona.anioresidencia} años y
								{eMigrantePersona.mesresidencia} meses
							{:else}
								S/T
							{/if}
						</h6>
					</div>
					<div class="col">
						<!-- Custom Switch -->
						<span class="fs-6">Fecha de salida:</span>
						<h6 class="mb-0">{eMigrantePersona.fecharetorno ?? 'S/F'}</h6>
					</div>
					<div class="col">
						{#if eMigrantePersona.download_archivo}
							<span class="fs-6">
								Certificado:
								<a
									href="javascript:;"
									class=""
									on:click={() => view_pdf(eMigrantePersona.download_archivo)}
									id="Tooltip_certificado"
								>
									<i class="bi bi-eye text-warning" />
								</a>

								<Tooltip target="Tooltip_certificado" placement="top"
									>Visualizar certificado</Tooltip
								>
								{#if eMigrantePersona.estadoarchivo_display === 'VALIDADO'}
									<span class="badge-dot bg-success" id="Tooltip_certificado_estado">VALIDADO</span>
								{:else if eMigrantePersona.estadoarchivo_display === 'RECHAZADO'}
									<span class="badge-dot bg-danger" id="Tooltip_certificado_estado">RECHAZADO</span>
								{:else}
									<span class="badge-dot bg-secondary" id="Tooltip_certificado_estado">CARGADO</span
									>
								{/if}
								<Tooltip target="Tooltip_certificado_estado" placement="top"
									>Estado de archivo: {eMigrantePersona.estadoarchivo_display}</Tooltip
								>
							</span>
						{:else}
							<span class="fs-6"> Certificado: </span>
							<h6 class="mb-0">S/C</h6>
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
