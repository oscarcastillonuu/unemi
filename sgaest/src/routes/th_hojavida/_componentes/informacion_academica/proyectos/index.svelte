<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	import Swal from 'sweetalert2';
	import { apiPOST } from '$lib/utils/requestUtils';
	import { addToast } from '$lib/store/toastStore';
	import { html } from 'gridjs';
	import { Tooltip } from 'sveltestrap';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let mView = false;
	let eProyectos = [];
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eProyectos = aData.eProyectos ?? [];
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		/*if (action == 'saveFormacionAcademicaCertificacion') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_9');
			menu.click();
		}*/
	};

	const openModal = (component, title, data, isView) => {
		modalDetalleContent = component;
		mOpenModal = !mOpenModal;
		aDataModal = { ...data };
		mTitleModal = title;
		mSizeModal = 'md';
		mView = isView;
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

{#if eProyectos}
	<div class="row">
		<div class="col-12">
			<div class="card ">
				<div class="card-header d-lg-flex justify-content-between align-items-center">
					<div class="headtitle mb-lg-0 m-0">
						<h3 class="mx-2 m-0 p-0">Proyectos</h3>
						<h6 class="mx-2 m-0 p-0">Listado de proyectos registrados</h6>
					</div>
				</div>
				<div class="card-body" tabindex="-1">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive table-hover table-centered">
							<thead class="table-light">
								<tr class="">
									<th class="text-center align-middle p-1" scope="col" style="width:40%;">
										Programa
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:40%;">
										Proyecto
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Tipo
									</th>
									<th class="text-center align-middle p-1" scope="col" style="width:10%;">
										Horas
									</th>
								</tr>
							</thead>
							<tbody>
								{#if eProyectos.length}
									{#each eProyectos as eProyecto}
										<tr class="">
											<td class="text-center align-middle p-1 fs-6">
												{eProyecto.programa ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eProyecto.proyecto ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eProyecto.tipo ?? ''}
											</td>
											<td class="text-center align-middle p-1 fs-6">
												{eProyecto.horas ?? 0}
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="4" class="text-center">No existe registro de proyectos</td>
									</tr>
								{/if}
							</tbody>
						</table>
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
		mTitle={mTitleModal}
		mSize={mSizeModal}
		mClass={mClassModal}
		{mOpenModal}
		{mView}
		on:actionRun={actionRun}
	/>
{/if}
