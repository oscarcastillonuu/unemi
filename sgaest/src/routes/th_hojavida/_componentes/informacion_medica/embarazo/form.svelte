<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	let ePersonaDetalleMaternidad;
	const dispatch = createEventDispatcher();
	const flatpickrFechaInicioEmbarazoOptions = {
		element: '#id_fechainicioembarazo_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const flatpickrFechaPartoOptions = {
		element: '#id_fechaparto_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputFechaInicioEmbarazo = '';
	let inputFechaParto = '';
	let inputSemanasEmbarazo = 0;
	let inputLactancia = false;
	let inputGestacion = false;

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePersonaDetalleMaternidad = aData.ePersonaDetalleMaternidad;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (ePersonaDetalleMaternidad) {
			inputFechaInicioEmbarazo = ePersonaDetalleMaternidad.fechainicioembarazo ?? '';
			inputFechaParto = ePersonaDetalleMaternidad.fechaparto ?? '';
			inputSemanasEmbarazo = ePersonaDetalleMaternidad.semanasembarazo ?? 0;
			inputLactancia = ePersonaDetalleMaternidad.lactancia ?? false;
			inputGestacion = ePersonaDetalleMaternidad.gestacion ?? false;
		}

		await delay(2000);
		load = false;
	});

	const saveDatosPersonalesEmbarazo = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatoEmbarazo = document.getElementById('frmDatoEmbarazo');
		const formData = new FormData($frmDatoEmbarazo);
		const fechainicioembarazo = document.getElementById('id_fechainicioembarazo');
		const fechaparto = document.getElementById('fechaparto');
		formData.append('gestacion', inputGestacion ? 'true' : 'false');
		formData.append('lactancia', inputLactancia ? 'true' : 'false');
		if (fechainicioembarazo) {
			formData.append('fechainicioembarazo', fechainicioembarazo.value);
		}
		if (fechaparto) {
			formData.append('fechaparto', fechaparto.value);
		}
		formData.append('semanasembarazo', inputSemanasEmbarazo.toString());
		if (ePersonaDetalleMaternidad != undefined) {
			formData.append('id', ePersonaDetalleMaternidad.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('action', 'saveDatosPersonalesEmbarazo');
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/hoja_vida', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			loading.setLoading(false, 'Cargando, espere por favor...');
			if (!res.isSuccess) {
				addToast({ type: 'error', header: '¡ERROR!', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				if (res.data.form) {
					await customFormErrors(res.data.form);
				}

				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				dispatch('actionRun', { action: 'saveDatosPersonalesEmbarazo' });
			}
		}
	};
</script>

<Modal
	isOpen={true}
	toggle={mToggle}
	size="md"
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
	backdrop="static"
>
	<ModalHeader toggle={mToggle} class="bg-primary text-white">
		<span class="text-white">{mTitle}</span>
	</ModalHeader>
	<ModalBody>
		{#if !load}
			<form action="javascript:;" id="frmDatoEmbarazo">
				<div class="row g-3">
					<div class="col-md-7 col-12">
						<label for="id_fechainicioembarazo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Inicio de gestación:</label
						>
						<Flatpickr
							options={flatpickrFechaInicioEmbarazoOptions}
							bind:value={inputFechaInicioEmbarazo}
							element="#id_fechainicioembarazo_element"
						>
							<div class="flatpickr input-group" id="id_fechainicioembarazo_element">
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder="Seleccione una fecha..."
									data-input
									id="id_fechainicioembarazo"
								/>
								<span class="input-group-text text-muted" title="Fecha" data-toggle
									><i class="fe fe-calendar" /></span
								>
								<span class="input-group-text text-danger" title="clear" data-clear>
									<i class="fe fe-x" />
								</span>
							</div>
						</Flatpickr>
						<div class="valid-feedback" id="id_fechainicioembarazo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-md-5 col-12">
						<label for="id_semanasembarazo" class="form-label fw-bold"
							><span><i class="fe fe-alert-octagon text-warning" /></span> Semanas de Embarazo:</label
						>
						<input
							type="number"
							class="form-control form-control-sm"
							id="id_semanasembarazo"
							bind:value={inputSemanasEmbarazo}
						/>
						<div class="valid-feedback" id="id_semanasembarazo_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="id_gestacion"
								bind:checked={inputGestacion}
							/>
							<label class="form-check-label fw-bold text-dark" for="id_gestacion"
								>¿Se escuentra en estado de gestación?</label
							>
						</div>
						<div class="valid-feedback" id="id_gestacion_validate">¡Se ve bien!</div>
					</div>
					<div class="col-12">
						<div class="form-check form-switch">
							<input
								class="form-check-input"
								type="checkbox"
								id="id_lactancia"
								bind:checked={inputLactancia}
							/>
							<label class="form-check-label fw-bold text-dark" for="id_lactancia"
								>¿Se escuentra en periodo de lactancia?</label
							>
						</div>
						<div class="valid-feedback" id="id_lactancia_validate">¡Se ve bien!</div>
					</div>
					{#if inputGestacion}
						<div class="col-12">
							<label for="id_fechaparto" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha de parto:</label
							>
							<Flatpickr
								options={flatpickrFechaPartoOptions}
								bind:value={inputFechaParto}
								element="#id_fechaparto_element"
							>
								<div class="flatpickr input-group" id="id_fechaparto_element">
									<input
										type="text"
										class="form-control form-control-sm"
										placeholder="Seleccione una fecha..."
										data-input
										id="id_fechaparto"
									/>
									<span class="input-group-text text-muted" title="Fecha" data-toggle
										><i class="fe fe-calendar" /></span
									>
									<span class="input-group-text text-danger" title="clear" data-clear>
										<i class="fe fe-x" />
									</span>
								</div>
							</Flatpickr>
							<div class="valid-feedback" id="id_fechaparto_validate">¡Se ve bien!</div>
						</div>
					{/if}
				</div>
			</form>
		{:else}
			<div class="m-0 my-5 justify-content-center align-items-center">
				<div class="text-center align-middle">
					<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
					<h3>{mensaje_load}</h3>
				</div>
			</div>
		{/if}
	</ModalBody>
	<ModalFooter>
		{#if !load}
			<Button color="warning" class="rounded-5 btn-sm" on:click={saveDatosPersonalesEmbarazo}
				><i class="fe fe-check" /> Guardar</Button
			>
		{/if}
		<Button color="secondary" class="rounded-5 btn-sm " on:click={mToggle}
			><i class="fe fe-x" /> Cancelar</Button
		>
	</ModalFooter>
</Modal>

<style>
	.form-select {
		border-color: #aaa;
	}
	.form-control {
		border-color: #aaa;
	}
</style>
