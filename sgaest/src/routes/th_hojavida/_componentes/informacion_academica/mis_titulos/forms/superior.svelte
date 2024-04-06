<script lang="ts">
	import FormSelectSearch from '$components/Formulario/SelectSearch.svelte';
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import {
		getTitulos as loadDataTitulos,
		getAreasTitulos as loadDataAreas,
		getInstitucionesEducacionSuperiores as loadDataUniversidades,
		getPaises as loadDataPaises,
		getProvinicias as loadDataProvincias,
		getCantones as loadDataCantones,
		getParroquias as loadDataParroquias
	} from '$lib/utils/loadDataApi';
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
	export let mSize = 'lg';
	export let mOpenModal;
	export let mView = false;
	const FechaInicioOptions = {
		element: '#id_fechainicio_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const FechaObtencionOptions = {
		element: '#id_fechaobtencion_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const FechaEgresadoOptions = {
		element: '#id_fechaegresado_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	const FechaRegistroOptions = {
		element: '#id_fecharegistro_element',
		locale: Spanish,
		dateFormat: 'Y-m-d'
	};
	let eSuperior;
	let readSelectionTitulo;
	let readSelectionArea;
	let readSelectionInstitcuion;
	let readSelectionPais;
	let readSelectionProvincia;
	let readSelectionCanton;
	let readSelectionParroquia;
	let bloqueo = false;
	let download_archivo = '';
	let download_registroarchivo = '';
	let fileArchivoTitulo;
	let fileArchivoSenescyt;
	let inputFechaInicio;
	let inputFechaObtencion;
	let inputFechaEgresado;
	let inputFechaRegistro;
	let inputRegistro;
	let inputCursando = false;
	const dispatch = createEventDispatcher();

	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	onMount(async () => {
		eSuperior = aData.eSuperior ?? {};
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		if (eSuperior) {
			if (eSuperior.titulo) {
				readSelectionTitulo = {
					id: eSuperior.titulo['pk'],
					name: eSuperior.titulo['nombre']
				};
			}

			if (eSuperior.areatitulo) {
				readSelectionArea = {
					id: eSuperior.areatitulo['pk'],
					name: eSuperior.areatitulo['nombre']
				};
			}

			if (eSuperior.institucion) {
				readSelectionInstitcuion = {
					id: eSuperior.institucion['pk'],
					name: eSuperior.institucion['nombre']
				};
			}
			bloqueo = eSuperior.verificadosenescyt ?? false;

			if (eSuperior.pais) {
				readSelectionPais = {
					id: eSuperior.pais['pk'],
					name: eSuperior.pais['nombre']
				};
			}
			if (eSuperior.provincia) {
				readSelectionProvincia = {
					id: eSuperior.provincia['pk'],
					name: eSuperior.provincia['nombre']
				};
			}
			if (eSuperior.canton) {
				readSelectionCanton = {
					id: eSuperior.canton['pk'],
					name: eSuperior.canton['nombre']
				};
			}
			if (eSuperior.parroquia) {
				readSelectionParroquia = {
					id: eSuperior.parroquia['pk'],
					name: eSuperior.parroquia['nombre']
				};
			}
			inputFechaInicio = eSuperior.fechainicio ?? '';
			inputFechaObtencion = eSuperior.fechaobtencion ?? '';
			inputFechaEgresado = eSuperior.fechaegresado ?? '';
			inputCursando = eSuperior.cursando ?? false;
			inputRegistro = eSuperior.registro ?? '';
			inputFechaRegistro = eSuperior.fecharegistro ?? '';
			download_archivo = eSuperior.download_archivo ?? '';
			download_registroarchivo = eSuperior.download_registroarchivo ?? '';
		}
		mensaje_load = 'Cargando la información, espere por favor...';

		await delay(2000);
		load = false;
	});

	const saveFormacionAcademicaSuperior = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmBachiller = document.getElementById('frmBachiller');
		const formData = new FormData($frmBachiller);
		if (eSuperior != undefined) {
			formData.append('id', eSuperior.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		if (readSelectionTitulo != null) {
			formData.append('titulo', readSelectionTitulo.id);
		}
		if (readSelectionArea != null) {
			formData.append('areatitulo', readSelectionArea.id);
		}
		if (readSelectionInstitcuion != null) {
			formData.append('institucion', readSelectionInstitcuion.id);
		}
		if (readSelectionPais != null) {
			formData.append('pais', readSelectionPais.id);
		}
		if (readSelectionProvincia != null) {
			formData.append('provincia', readSelectionProvincia.id);
		}
		if (readSelectionCanton != null) {
			formData.append('canton', readSelectionCanton.id);
		}
		if (readSelectionParroquia != null) {
			formData.append('parroquia', readSelectionParroquia.id);
		}
		const fechainicio = document.getElementById('id_fechainicio');
		const fechaobtencion = document.getElementById('id_fechaobtencion');
		const fechaegresado = document.getElementById('id_fechaegresado');
		const fecharegistro = document.getElementById('id_fecharegistro');
		formData.append('fechainicio', fechainicio.value ?? '');
		formData.append('cursando', inputCursando ? 'true' : 'false');
		formData.append('fechaobtencion', fechaobtencion.value ?? '');
		formData.append('fechaegresado', fechaegresado.value ?? '');
		formData.append('fecharegistro', fecharegistro.value ?? '');
		formData.append('registro', inputRegistro);
		if (fileArchivoTitulo) {
			formData.append('archivo', fileArchivoTitulo.file);
		}
		if (fileArchivoSenescyt) {
			formData.append('registroarchivo', fileArchivoSenescyt.file);
		}

		formData.append('action', 'saveFormacionAcademicaSuperior');
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
				dispatch('actionRun', { action: 'saveFormacionAcademicaTitulo' });
			}
		}
	};

	const changeTitulo = (event) => {
		//console.log("change: ", event);
	};

	const changeInstitucion = (event) => {
		//console.log("change: ", event);
	};

	const changeArea = (event) => {
		//console.log("change: ", event);
	};

	const changePais = (event) => {
		//console.log("change pais: ", event);
		readSelectionProvincia = null;
		readSelectionCanton = null;
		readSelectionParroquia = null;
	};
	const changeProvincia = (event) => {
		//console.log("change provincia: ", event);
		readSelectionCanton = null;
		readSelectionParroquia = null;
	};
	const changeCanton = (event) => {
		//console.log("change canton: ", event);
		readSelectionParroquia = null;
	};

	const handleFileSelectedTitulo = (event) => {
		fileArchivoTitulo = event.detail;
	};

	const handleFileRemovedTitulo = () => {
		fileArchivoTitulo = null;
	};

	const handleFileSelectedSenescyt = (event) => {
		fileArchivoSenescyt = event.detail;
	};

	const handleFileRemovedSenescyt = () => {
		fileArchivoSenescyt = null;
	};
</script>

{#if eSuperior}
	<Modal isOpen={mOpenModal} toggle={mToggle} size={mSize} class={mClass} backdrop="static">
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmBachiller">
					<div class="row g-3">
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_titulo" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Título:</label
							>
							<FormSelectSearch
								inputId="id_titulo"
								name="titulo"
								bind:value={readSelectionTitulo}
								on:actionChangeSelectSearch={changeTitulo}
								disabled={bloqueo || mView}
								fetch={(query) =>
									loadDataTitulos(query, '2,3,4,15,16,17,18,19,20,21,22,26,27,29,30')}
							/>
							<div class="valid-feedback" id="id_titulo_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_institucion" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> IES:</label
							>
							<FormSelectSearch
								inputId="id_institucion"
								name="institucion"
								bind:value={readSelectionInstitcuion}
								on:actionChangeSelectSearch={changeInstitucion}
								disabled={bloqueo || mView}
								fetch={(query) => loadDataUniversidades(query)}
							/>
							<div class="valid-feedback" id="id_institucion_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-12 col-md-12 col-12 mb-1">
							<label for="id_areatitulo" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Area de titulación:</label
							>
							<FormSelectSearch
								inputId="id_areatitulo"
								name="areatitulo"
								bind:value={readSelectionArea}
								on:actionChangeSelectSearch={changeArea}
								disabled={mView}
								fetch={(query) => loadDataAreas(query)}
							/>
							<div class="valid-feedback" id="id_areatitulo_validate">¡Se ve bien!</div>
						</div>
					</div>
					<div class="row g-3 mt-1">
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_pais" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> País:</label
							>
							<FormSelectSearch
								inputId="id_pais"
								name="pais"
								bind:value={readSelectionPais}
								disabled={mView}
								on:actionChangeSelectSearch={changePais}
								fetch={(query) => loadDataPaises(query)}
							/>
							<div class="valid-feedback" id="id_pais_validate">¡Se ve bien!</div>
						</div>
						{#if readSelectionPais != null && readSelectionPais.id === 1}
							<div class="col-lg-6 col-md-6 col-12 mb-1">
								<label for="id_provincia" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Provincia:</label
								>
								<FormSelectSearch
									inputId="id_provincia"
									name="provincia"
									parent="id_pais"
									bind:value={readSelectionProvincia}
									disabled={mView}
									on:actionChangeSelectSearch={changeProvincia}
									fetch={(query) => loadDataProvincias(readSelectionPais.id, query)}
								/>
								<div class="valid-feedback" id="id_provincia_validate">¡Se ve bien!</div>
							</div>
							{#if readSelectionProvincia != null}
								<div class="col-lg-6 col-md-6 col-12 mb-1">
									<label for="id_canton" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Cantón:</label
									>
									<FormSelectSearch
										inputId="id_canton"
										name="canton"
										parent="id_provincia"
										bind:value={readSelectionCanton}
										disabled={mView}
										on:actionChangeSelectSearch={changeCanton}
										fetch={(query) => loadDataCantones(readSelectionProvincia.id, query)}
									/>
									<div class="valid-feedback" id="id_canton_validate">¡Se ve bien!</div>
								</div>
							{/if}
							{#if readSelectionCanton != null}
								<div class="col-lg-6 col-md-6 col-12 mb-1">
									<label for="id_parroquia" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Parroquia:</label
									>
									<FormSelectSearch
										inputId="id_parroquia"
										name="parroquia"
										parent="id_canton"
										bind:value={readSelectionParroquia}
										disabled={mView}
										fetch={(query) => loadDataParroquias(readSelectionCanton.id, query)}
									/>
									<div class="valid-feedback" id="id_parroquia_validate">¡Se ve bien!</div>
								</div>
							{/if}
						{/if}
					</div>
					<div class="row g-3 mt-1">
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_fechainicio" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Fecha inicio de estudios:</label
							>
							{#if mView}
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder=""
									data-input
									readonly={true}
									disabled={true}
									bind:value={inputFechaInicio}
									id="id_fechainicio"
								/>
							{:else}
								<Flatpickr
									options={FechaInicioOptions}
									bind:value={inputFechaInicio}
									element="#id_fechainicio_element"
								>
									<div class="flatpickr input-group" id="id_fechainicio_element">
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											id="id_fechainicio"
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
							<div class="valid-feedback" id="id_fechainicio_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_cursando"
									disabled={bloqueo || mView}
									bind:checked={inputCursando}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_cursando"
									>¿Está en curso?</label
								>
							</div>
							<div class="valid-feedback" id="id_cursando_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_fechaegresado" class="form-label fw-bold"
								>{#if !inputRegistro}<span><i class="fe fe-alert-octagon text-warning" /></span
									>{/if} Fecha de egreso:</label
							>
							{#if mView}
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder=""
									data-input
									readonly={true}
									disabled={true}
									bind:value={inputFechaEgresado}
									id="id_fechaegresado"
								/>
							{:else}
								<Flatpickr
									options={FechaEgresadoOptions}
									bind:value={inputFechaEgresado}
									element="#id_fechaegresado_element"
								>
									<div class="flatpickr input-group" id="id_fechaegresado_element">
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											id="id_fechaegresado"
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
							<div class="valid-feedback" id="id_fechaegresado_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_fechaobtencion" class="form-label fw-bold"
								>{#if !inputRegistro}<span><i class="fe fe-alert-octagon text-warning" /></span
									>{/if} Fecha de obtención:</label
							>
							{#if mView}
								<input
									type="text"
									class="form-control form-control-sm"
									placeholder=""
									data-input
									readonly={true}
									disabled={true}
									bind:value={inputFechaObtencion}
									id="id_fechaobtencion"
								/>
							{:else}
								<Flatpickr
									options={FechaObtencionOptions}
									bind:value={inputFechaObtencion}
									element="#id_fechaobtencion_element"
								>
									<div class="flatpickr input-group" id="id_fechaobtencion_element">
										<input
											type="text"
											class="form-control form-control-sm"
											placeholder=""
											data-input
											id="id_fechaobtencion"
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
							<div class="valid-feedback" id="id_fechaobtencion_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_registro" class="form-label fw-bold"
								>{#if !inputRegistro}<span><i class="fe fe-alert-octagon text-warning" /></span
									>{/if} Número de registro SENESCYT:</label
							>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_registro"
								disabled={bloqueo || mView}
								bind:value={inputRegistro}
							/>
							<div class="valid-feedback" id="id_registro_validate">¡Se ve bien!</div>
						</div>
						<div class="col-lg-6 col-md-6 col-12 mb-1">
							<label for="id_fecharegistro" class="form-label fw-bold"
								>{#if !inputRegistro}<span><i class="fe fe-alert-octagon text-warning" /></span
									>{/if} Fecha de registro SENESCYT:</label
							>
							<Flatpickr
								options={FechaRegistroOptions}
								bind:value={inputFechaRegistro}
								element="#id_fecharegistro_element"
							>
								<div class="flatpickr input-group" id="id_fecharegistro_element">
									<input
										type="text"
										class="form-control form-control-sm"
										placeholder=""
										data-input
										disabled={mView}
										readonly={mView}
										id="id_fecharegistro"
									/>
									{#if !mView}
										<span class="input-group-text text-muted" title="Fecha" data-toggle
											><i class="fe fe-calendar" /></span
										>
										<span class="input-group-text text-danger" title="clear" data-clear>
											<i class="fe fe-x" />
										</span>
									{/if}
								</div>
							</Flatpickr>
							<div class="valid-feedback" id="id_fecharegistro_validate">¡Se ve bien!</div>
						</div>
					</div>
					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-md-6 col-12">
							<label for="id_archivo" class="form-label fw-bold">Titulo:</label>
							{#if !mView}
								<FileUploader
									inputID="id_archivo"
									inputName="archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedTitulo}
									on:fileRemoved={handleFileRemovedTitulo}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if download_archivo != ''}
								<div class="fs-6">
									Tienes un titulo subido:
									<a
										title="Ver archivo"
										href={download_archivo}
										target="_blank"
										class="text-primary text-center">Ver titulo</a
									>
								</div>
							{:else if mView}
								<div class="fs-6">
									<p class="fw-bold text-danger">No tienes titulo subido</p>
								</div>
							{/if}

							<div class="valid-feedback" id="id_archivo_validate">¡Se ve bien!</div>
						</div>

						<div class="col-md-6 col-12">
							<label for="id_registroarchivo" class="form-label fw-bold">SENESCYT:</label>
							{#if !mView}
								<FileUploader
									inputID="id_registroarchivo"
									inputName="registroarchivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedSenescyt}
									on:fileRemoved={handleFileRemovedSenescyt}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if download_registroarchivo != ''}
								<div class="fs-6">
									Tienes un recocimiento académico subido:
									<a
										title="Ver archivo"
										href={download_registroarchivo}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{:else if mView}
								<div class="fs-6">
									<p class="fw-bold text-danger">No tienes archivo de SENESCYT subido</p>
								</div>
							{/if}

							<div class="valid-feedback" id="id_registroarchivo_validate">¡Se ve bien!</div>
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
				{#if !mView}
					<Button color="warning" class="rounded-5 btn-sm" on:click={saveFormacionAcademicaSuperior}
						><i class="fe fe-check" /> Guardar</Button
					>
				{:else}
					<Button
						type="button"
						color="primary"
						class="rounded-5 btn-sm"
						on:click={() => (mView = !mView)}><i class="fe fe-edit" /> Editar</Button
					>
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
