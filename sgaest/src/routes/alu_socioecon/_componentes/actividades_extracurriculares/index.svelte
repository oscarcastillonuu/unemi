<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ComponentHorasTareaHogar from './frmHorasTareaHogar.svelte';
	import ComponentHorasTrabajoHogar from './frmHorasTrabajoHogar.svelte';
	import ComponentHorasTrabajoFueraHogar from './frmHorasTrabajoFueraHogar.svelte';
	import ComponentTipoActividad from './frmTipoActividad.svelte';
	import ComponentHorasHacerTarea from './frmHorasHacerTareas.svelte';
	import ComponentTipoTarea from './frmTipoTarea.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { apiPOST, browserGet, browserSet, getCurrentRefresh } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { goto } from '$app/navigation';
	import { decodeToken } from '$lib/utils/decodetoken';
	import { userData } from '$lib/store/userStore';
	import { addToast } from '$lib/store/toastStore';
	import Swal from 'sweetalert2';
	import { addNotification } from '$lib/store/notificationStore';
	import { navigating } from '$app/stores';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	let modalTitle;
	export let aData;
	let aDataModal;
	let eFichaSocioeconomica = {};
	const dispatch = createEventDispatcher();
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			eFichaSocioeconomica = aData.eFichaSocioeconomica ?? {};
		}
	});

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosActividadExtracurricular') {
			const menu = document.getElementById('menu_element_13');
			menu.click();
			mOpenModal = !mOpenModal;
		}
	};

	const openModalGenerico = (componente, title) => {
		modalDetalleContent = componente;
		mOpenModal = !mOpenModal;
		modalTitle = title;
		aDataModal = { eFichaSocioeconomica: eFichaSocioeconomica };
	};

	const eliminarElemento = async (field, texto) => {
		const mensaje = {
			title: `${texto}`,
			html: `Esta acción es irreversible`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: `Si, deseo hacerlo!`,
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Procesando la información, espere por favor...');
					if (browserGet('refreshToken')) {
						const response = await getCurrentRefresh(
							fetch,
							`${variables.BASE_API_URI}/token/refresh`
						);
						if (response.status >= 400) {
							goto('/lock-screen');
						}
						if (response.ok == true) {
							const json = decodeToken(await response.json());
							browserSet('refreshToken', json.tokens.refresh);
							browserSet('accessToken', json.tokens.access);
							browserSet('dataSession', JSON.stringify(json));
							userData.set(json);
						}
					} else {
						goto('/login');
					}
					loading.setLoading(true, 'Eliminando la información, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/socioeconomica', {
						action: 'deleteActividadExtracurricular',
						field: field
					});
					loading.setLoading(false, 'Eliminando la información, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						loading.setLoading(false, 'Cargando, espere por favor...');
						return;
					} else {
						loading.setLoading(false, 'Cargando, espere por favor...');
						if (!res.isSuccess) {
							addToast({ type: 'error', header: '¡ERROR!', body: res.message });
							return;
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se elimino correctamente la información'
							});
							const menu = document.getElementById('menu_element_13');
							menu.click();
						}
					}
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({
						msg: 'Enhorabuena el registro esta salvado.!',
						type: 'info'
					});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({
					msg: error.message,
					type: 'error'
				});
			});
	};
</script>

<div class="card border-0 mx-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Actividades extracurriculares</h3>
			<p class="mb-0">Tiempo que dedicas a cada actividad</p>
		</div>
		<!--<div>
				<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
			</div>-->
	</div>
	<div class="card-body">
		<div class="bg-light rounded border-1 p-2 mb-4">
			<div class="list-group list-group-flush border-1 ">
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Tareas en el hogar</span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.horastareahogar}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentHorasTareaHogar, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'horastareahogar',
											'¿Estas a punto de eliminar el tiempo de tareas en el hogar?'
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentHorasTareaHogar, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.horastareahogar > 0}
						<div class="p-2">
							<span class="text-primary fs-6">Horas: {eFichaSocioeconomica.horastareahogar}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle">Trabajo doméstico </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.horastrabajodomestico}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentHorasTrabajoHogar, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'horastrabajodomestico',
											`¿Estas a punto de eliminar cantidad de horas de trabajo doméstico?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentHorasTrabajoHogar, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.horastrabajodomestico > 0}
						<div class="p-2">
							<span class="text-primary fs-6">Horas: {eFichaSocioeconomica.horastrabajodomestico}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"> Trabajo fuera de casa </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.horastrabajofuera}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentHorasTrabajoFueraHogar, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'horastrabajofuera',
											`¿Estas a punto de eliminar cantidad de horas de trabajo fuera de casa?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentHorasTrabajoFueraHogar, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.horastrabajofuera > 0}
						<div class="p-2">
							<span class="text-primary fs-6">Horas: {eFichaSocioeconomica.horastrabajofuera}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"> Actividades de recreación </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.tipoactividad}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentTipoActividad, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'tipoactividad',
											`¿Estas a punto de eliminar el dato del material predominante en el piso?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentTipoActividad, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.tipoactividad}
						<div class="p-2">
							<span class="text-primary fs-6"
								>{eFichaSocioeconomica.tipoactividad_display}{#if eFichaSocioeconomica.tipoactividad == 7 && eFichaSocioeconomica.tipoactividad != ''}
									: {eFichaSocioeconomica.otrosactividad}
								{/if}</span
							>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"
								>¿Cuanto tiempo promedio se dedica para hacer sus tareas?
							</span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.horashacertareas}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentHorasHacerTarea, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'horashacertareas',
											`¿Estas a punto de eliminar tiempo promedio que dedica para hacer tareas?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentHorasHacerTarea, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.horashacertareas > 0}
						<div class="p-2">
							<span class="text-primary fs-6">Horas: {eFichaSocioeconomica.horashacertareas}</span>
						</div>
					{/if}
				</div>
				<div class="list-group-item border-1 rounded px-3 text-nowrap mb-1">
					<div class="d-flex align-items-center justify-content-between">
						<h5 class="mb-0 text-truncate">
							<span class="align-middle"> ¿Donde realiza las tareas? </span>
						</h5>
						<div>
							{#if eFichaSocioeconomica.tipotarea}
								<a
									href="javascript:void(0);"
									class="me-1 text-inherit text-warning"
									aria-label="Editar"
									on:click={() => openModalGenerico(ComponentTipoTarea, 'Actualizar')}
									data-bs-original-title="Edit"><i class="fe fe-edit fw-bold fs-5" /></a
								>
								<a
									href="#"
									class="me-1 text-inherit text-danger"
									aria-label="Eliminar"
									on:click={() =>
										eliminarElemento(
											'tipotarea',
											`¿Estas a punto de eliminar el dato de donde realiza las tareas?`
										)}
									data-bs-original-title="Delete"><i class="fe fe-trash-2 fw-bold fs-5" /></a
								>
							{:else}
								<a
									href="javascript:void(0);"
									on:click={() => openModalGenerico(ComponentTipoTarea, 'Adicionar')}
									class="me-1 text-inherit text-success"
									aria-label="Adicionar"
									data-bs-original-title="Edit"><i class="fe fe-plus fw-bold fs-5" /></a
								>
							{/if}
						</div>
					</div>
					{#if eFichaSocioeconomica.tipotarea}
						<div class="p-2">
							<span class="text-primary fs-6"
								>{eFichaSocioeconomica.tipotarea_display}{#if eFichaSocioeconomica.tipotarea == 8 && eFichaSocioeconomica.tipotarea != ''}
									: {eFichaSocioeconomica.otrostarea}
								{/if}</span
							>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>
{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mTitle={modalTitle}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
{/if}
