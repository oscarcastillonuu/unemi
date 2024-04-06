<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { cleave } from 'svelte-cleavejs'; //https://github.com/nosir/cleave.js/blob/master/doc/options.md
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import 'flatpickr/dist/themes/light.css';
	import { Spanish } from '$dist/flatpickr/src/l10n/es';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
	export let mSize = 'md';
	export let mOpenModal;
	export let mView = false;
	const FechaDesdeOptions = {
		element: '#id_fechadesde_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const FechaHastaOptions = {
		element: '#id_fechahasta_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};

	let eCertificacion;
	let bloqueo = false;
	let inputAutoridadEmisora = '';
	let inputNombres = '';
	let inputNumeroLicencia = '';
	let inputFechaDesde;
	let inputFechaHasta;
	let inputEnlace = '';
	let inputVigente = false;
	let inputVerificado = false;
	let download_archivo = '';
	let fileArchivo;
	const dispatch = createEventDispatcher();

	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	onMount(async () => {
		eCertificacion = aData.eCertificacion ?? {};
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		if (eCertificacion) {
			inputAutoridadEmisora = eCertificacion.autoridad_emisora ?? '';
			inputNombres = eCertificacion.nombres ?? '';
			inputNumeroLicencia = eCertificacion.numerolicencia ?? '';
			inputFechaDesde = eCertificacion.fechadesde ?? '';
			inputFechaHasta = eCertificacion.fechahasta ?? '';
			inputEnlace = eCertificacion.enlace ?? '';
			download_archivo = eCertificacion.download_archivo ?? '';
			inputVigente = eCertificacion.vigente ?? false;
			inputVerificado = eCertificacion.verificado ?? false;
			bloqueo = inputVerificado;
		}
		mensaje_load = 'Cargando la información, espere por favor...';

		await delay(2000);
		load = false;
	});

	const saveFormacionAcademicaCertificacion = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmCertificacion = document.getElementById('frmCertificacion');
		const formData = new FormData($frmCertificacion);
		if (eCertificacion != undefined) {
			formData.append('id', eCertificacion.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('nombres', inputNombres ?? '');
		formData.append('autoridad_emisora', inputAutoridadEmisora ?? '');
		formData.append('numerolicencia', inputNumeroLicencia ?? '');

		const fechadesde = document.getElementById('id_fechadesde');
		const fechahasta = document.getElementById('id_fechahasta');
		if (fechadesde) {
			formData.append('fechadesde', fechadesde.value ?? '');
		}
		if (fechahasta) {
			formData.append('fechahasta', fechahasta.value ?? '');
		}

		formData.append('enlace', inputEnlace ?? '');
		formData.append('vigente', inputVigente ? 'true' : 'false');

		if (fileArchivo) {
			formData.append('archivo', fileArchivo.file);
		}

		formData.append('action', 'saveFormacionAcademicaCertificacion');
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
				dispatch('actionRun', { action: 'saveFormacionAcademicaCertificacion' });
			}
		}
	};

	const handleFileSelectedArchivo = (event) => {
		fileArchivo = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileArchivo = null;
	};

	const actionEdit = () => {
		mView = !mView;
		mTitle = `Editar certificación ${eCertificacion.nombres}`;
	};
</script>

{#if eCertificacion}
	<Modal isOpen={mOpenModal} toggle={mToggle} size={mSize} class={mClass} backdrop="static">
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmCertificacion">
					<div class="row g-3">
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_nombres" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Nombre de la certificación:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_nombres"
								disabled={bloqueo || mView}
								bind:value={inputNombres}
							/>
							<div class="valid-feedback" id="id_nombres_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_autoridad_emisora" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Autoridad emisora de la
								certificación:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_autoridad_emisora"
								disabled={bloqueo || mView}
								bind:value={inputAutoridadEmisora}
							/>
							<div class="valid-feedback" id="id_autoridad_emisora_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_numerolicencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Número de la licencia:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_numerolicencia"
								disabled={bloqueo || mView}
								bind:value={inputNumeroLicencia}
							/>
							<div class="valid-feedback" id="id_numerolicencia_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_enlace" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> URL de la certificación:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_enlace"
								disabled={bloqueo || mView}
								bind:value={inputEnlace}
							/>
							<div class="valid-feedback" id="id_enlace_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_vigente"
									disabled={bloqueo || mView}
									bind:checked={inputVigente}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_vigente"
									>¿Está certificación nunca expira?</label
								>
							</div>
							<div class="valid-feedback" id="id_vigente_validate">¡Se ve bien!</div>
						</div>

						<div class={inputVigente ? 'col-12 mb-1' : 'col-lg-6 col-md-6 col-12 mb-1'}>
							<label for="id_fechadesde" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha desde:</label
							>
							{#if mView}
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder=""
									data-input
									readonly={true}
									disabled={true}
									bind:value={inputFechaDesde}
									id="id_fechadesde"
								/>
							{:else}
								<Flatpickr
									options={FechaDesdeOptions}
									bind:value={inputFechaDesde}
									element="#id_fechadesde_element"
								>
									<div class="flatpickr input-group" id="id_fechadesde_element">
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											id="id_fechadesde"
										/>

										<span class="input-group-text text-muted" title="Fecha" data-toggle
											><i class="fe fe-calendar" /></span
										>
										<span class="input-group-text text-danger" title="clear" data-clear>
											<i class="fe fe-x" />
										</span>
									</div>
								</Flatpickr>
							{/if}
							<div class="valid-feedback" id="id_fechadesde_validate">¡Se ve bien!</div>
						</div>

						{#if !inputVigente}
							<div class="col-lg-6 col-md-6 col-12 mb-1">
								<label for="id_fechahasta" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha hasta:</label
								>
								{#if mView}
									<input
										type="text"
										class="form-control form-control-sm"
										placeholder=""
										data-input
										readonly={true}
										disabled={true}
										bind:value={inputFechaDesde}
										id="id_fechahasta"
									/>
								{:else}
									<Flatpickr
										options={FechaHastaOptions}
										bind:value={inputFechaHasta}
										element="#id_fechahasta_element"
									>
										<div class="flatpickr input-group" id="id_fechahasta_element">
											<input
												type="text"
												class="form-control form-control-sm"
												placeholder=""
												data-input
												id="id_fechahasta"
											/>

											<span class="input-group-text text-muted" title="Fecha" data-toggle
												><i class="fe fe-calendar" /></span
											>
											<span class="input-group-text text-danger" title="clear" data-clear>
												<i class="fe fe-x" />
											</span>
										</div>
									</Flatpickr>
								{/if}
								<div class="valid-feedback" id="id_fechahasta_validate">¡Se ve bien!</div>
							</div>
						{/if}
					</div>

					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-12">
							<label for="id_archivo" class="form-label fw-bold">Archivo:</label>
							{#if !mView}
								<FileUploader
									inputID="id_archivo"
									inputName="archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedArchivo}
									on:fileRemoved={handleFileRemovedArchivo}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if download_archivo != ''}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={download_archivo}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{:else if mView}
								<div class="fs-6">
									<p class="fw-bold text-danger">No tienes archivo subido</p>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivo_validate">¡Se ve bien!</div>
						</div>
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
				{#if !eCertificacion.verificado}
					{#if !mView}
						<Button
							color="warning"
							class="rounded-5 btn-sm"
							on:click={saveFormacionAcademicaCertificacion}
							><i class="fe fe-check" /> Guardar</Button
						>
					{:else if !bloqueo}
						<Button type="button" color="primary" class="rounded-5 btn-sm" on:click={actionEdit}
							><i class="fe fe-edit" /> Editar</Button
						>
					{/if}
				{/if}
			{/if}
			<Button color="secondary" class="rounded-5 btn-sm" on:click={mToggle}
				><i class="fe fe-x" /> Cancelar</Button
			>
		</ModalFooter>
	</Modal>
{/if}

<style>
	.form-select {
		border-color: #aaa;
	}
	.form-control {
		border-color: #aaa;
	}
</style>
