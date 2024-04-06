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
	import {
		getInstitucionesCertificadoras as loadDataInstitucionesCertificadoras,
		getNivelesSuficiencias as loadDataNivelesSuficiencias,
		getIdiomas as loadDataIdiomas
	} from '$lib/utils/loadDataApi';
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
	const FechaCertificacionOptions = {
		element: '#id_fechacerti_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};

	let eCertificacion;
	let eIdiomas;
	let eInstituciones;
	let eNiveles;
	let selectIdioma = 0;
	let selectInstitucion = 0;
	let selectNivel = 0;
	let bloqueo = false;
	let inputValidaInstitucion = false;
	let inputOtraInstitucion = '';
	let inputFechaCertificacion;
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
		eInstituciones = await loadDataInstitucionesCertificadoras('');
		eNiveles = await loadDataNivelesSuficiencias('');
		eIdiomas = await loadDataIdiomas('');
		await delay(1000);
		if (eCertificacion) {
			if (eCertificacion.idioma) {
				selectIdioma = eCertificacion.idioma.pk ?? 0;
			}
			if (eCertificacion.institucioncerti) {
				selectInstitucion = eCertificacion.institucioncerti.pk ?? 0;
			}
			if (eCertificacion.nivelsuficencia) {
				selectNivel = eCertificacion.nivelsuficencia.pk ?? 0;
			}

			inputValidaInstitucion = eCertificacion.validainst ?? false;
			inputOtraInstitucion = eCertificacion.otrainstitucion ?? '';
			inputFechaCertificacion = eCertificacion.fechacerti ?? '';
			download_archivo = eCertificacion.download_archivo ?? '';
			bloqueo = eCertificacion.estado === 1;
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
		formData.append('idioma', selectIdioma.toString());
		if (inputValidaInstitucion) {
			formData.append('otrainstitucion', inputOtraInstitucion);
		} else {
			formData.append('institucioncerti', selectInstitucion.toString());
		}

		formData.append('nivelsuficencia', selectNivel.toString());
		formData.append('validainst', inputValidaInstitucion ? 'true' : 'false');

		const fechaCertificacion = document.getElementById('id_fechacerti');
		if (fechaCertificacion) {
			formData.append('fechacerti', fechaCertificacion.value ?? '');
		}
		if (fileArchivo) {
			formData.append('archivo', fileArchivo.file);
		}
		formData.append('action', 'saveFormacionAcademicaIdioma');
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
		mTitle = `Editar certificación ${eCertificacion.idioma.nombre}`;
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
							<label for="id_institucioncerti" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Institución Certificadora:</label
							>
							{#if eInstituciones}
								<select
									class="form-select form-select-sm"
									aria-label=""
									disabled={mView}
									id="id_institucioncerti"
									bind:value={selectInstitucion}
								>
									<option value={0} selected> ----------- </option>
									{#each eInstituciones as eInstitucion}
										{#if selectInstitucion === eInstitucion.id}
											<option value={eInstitucion.id} selected>
												{eInstitucion.name}
											</option>
										{:else}
											<option value={eInstitucion.id}>
												{eInstitucion.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_institucioncerti_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_validainst"
									disabled={bloqueo || mView}
									bind:checked={inputValidaInstitucion}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_validainst"
									>¿Es otra institución?</label
								>
							</div>
							<div class="valid-feedback" id="id_validainst_validate">¡Se ve bien!</div>
						</div>
						{#if inputValidaInstitucion}
							<div class="col-lg-12 col-md-12 col-12 mb-1">
								<label for="id_otrainstitucion" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Digite Institución:</label
								>
								<input
									type="text"
									class="form-control form-control-sm"
									id="id_otrainstitucion"
									disabled={bloqueo || mView}
									bind:value={inputOtraInstitucion}
								/>
								<div class="valid-feedback" id="id_otrainstitucion_validate">¡Se ve bien!</div>
							</div>
						{/if}
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_idioma" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Idioma:</label
							>
							{#if eIdiomas}
								<select
									class="form-select form-select-sm"
									aria-label=""
									disabled={bloqueo || mView}
									id="id_idioma"
									bind:value={selectIdioma}
								>
									<option value={0} selected> ----------- </option>
									{#each eIdiomas as eIdioma}
										{#if selectIdioma === eIdioma.id}
											<option value={eIdioma.id} selected>
												{eIdioma.name}
											</option>
										{:else}
											<option value={eIdioma.id}>
												{eIdioma.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_idioma_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_nivelsuficencia" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Nivel de Suficencia:</label
							>
							{#if eNiveles}
								<select
									class="form-select form-select-sm"
									aria-label=""
									disabled={bloqueo || mView}
									id="id_nivelsuficencia"
									bind:value={selectNivel}
								>
									<option value={0} selected> ----------- </option>
									{#each eNiveles as eNivel}
										{#if selectNivel === eNivel.id}
											<option value={eNivel.id} selected>
												{eNivel.name}
											</option>
										{:else}
											<option value={eNivel.id}>
												{eNivel.name}
											</option>
										{/if}
									{/each}
								</select>
							{/if}
							<div class="valid-feedback" id="id_nivelsuficencia_validate">¡Se ve bien!</div>
						</div>

						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_fechacerti" class="form-label fw-bold"
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
									bind:value={inputFechaCertificacion}
									id="id_fechacerti"
								/>
							{:else}
								<Flatpickr
									options={FechaCertificacionOptions}
									bind:value={inputFechaCertificacion}
									element="#id_fechacerti_element"
								>
									<div class="flatpickr input-group" id="id_fechacerti_element">
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											id="id_fechacerti"
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
							<div class="valid-feedback" id="id_fechacerti_validate">¡Se ve bien!</div>
						</div>
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
				{#if eCertificacion.estado != 1}
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
