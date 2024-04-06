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
		getColegios as loadDataColegios
	} from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { cleave } from 'svelte-cleavejs'; //https://github.com/nosir/cleave.js/blob/master/doc/options.md
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
	export let mSize = 'lg';
	export let mOpenModal;
	export let mView = false;
	let eBachiller;
	let readSelectionTitulo;
	let readSelectionColegio;
	let bloqueo = false;
	let inputCalificacion;
	let inputAnioInicio;
	let inputAnioFin;
	let download_actagrado = '';
	let download_reconocimientoacademico = '';
	let fileActaGrado;
	let fileReconocimiento;
	const dispatch = createEventDispatcher();

	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));

	onMount(async () => {
		eBachiller = aData.eBachiller ?? {};
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		if (eBachiller) {
			if (eBachiller.titulo) {
				readSelectionTitulo = {
					id: eBachiller.titulo['pk'],
					name: eBachiller.titulo['nombre']
				};
			}
			if (eBachiller.colegio) {
				readSelectionColegio = {
					id: eBachiller.colegio['pk'],
					name: eBachiller.colegio['nombre']
				};
			}
			if (eBachiller.detalletitulacionbachiller) {
				const eDetalleTitulacionBachiller = eBachiller.detalletitulacionbachiller;
				inputCalificacion = eDetalleTitulacionBachiller.calificacion ?? 0;
				inputAnioInicio = eDetalleTitulacionBachiller.anioinicioperiodograduacion ?? 0;
				inputAnioFin = eDetalleTitulacionBachiller.aniofinperiodograduacion ?? 0;
				download_actagrado = eDetalleTitulacionBachiller.download_actagrado ?? '';
				download_reconocimientoacademico =
					eDetalleTitulacionBachiller.download_reconocimientoacademico ?? '';
				bloqueo =
					(eDetalleTitulacionBachiller.codigorefrendacion &&
						eDetalleTitulacionBachiller.fechagrado) ??
					false;
			}
		}
		mensaje_load = 'Cargando la información, espere por favor...';

		await delay(2000);
		load = false;
	});

	const saveFormacionAcademicaBachiller = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmBachiller = document.getElementById('frmBachiller');
		const formData = new FormData($frmBachiller);
		if (eBachiller != undefined) {
			formData.append('id', eBachiller.pk ?? '0');
			if (eBachiller.detalletitulacionbachiller) {
				formData.append('idd', eBachiller.detalletitulacionbachiller.pk ?? '0');
			}
		} else {
			formData.append('id', '0');
			formData.append('idd', '0');
		}
		if (readSelectionTitulo != null) {
			formData.append('titulo', readSelectionTitulo.id);
		}
		if (readSelectionColegio != null) {
			formData.append('colegio', readSelectionColegio.id);
		}
		formData.append('calificacion', inputCalificacion);
		formData.append('anioinicioperiodograduacion', inputAnioInicio);
		formData.append('aniofinperiodograduacion', inputAnioFin);
		if (fileActaGrado) {
			formData.append('actagrado', fileActaGrado.file);
		}
		if (fileReconocimiento) {
			formData.append('reconocimientoacademico', fileReconocimiento.file);
		}
		formData.append('action', 'saveFormacionAcademicaBachiller');
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

	const changeColegio = (event) => {
		//console.log("change: ", event);
	};

	const handleFileSelectedActaGrado = (event) => {
		fileActaGrado = event.detail;
	};

	const handleFileRemovedActaGrado = () => {
		fileActaGrado = null;
	};

	const handleFileSelectedReconocimiento = (event) => {
		fileReconocimiento = event.detail;
	};

	const handleFileRemovedReconocimiento = () => {
		fileReconocimiento = null;
	};
</script>

{#if eBachiller}
	<Modal isOpen={mOpenModal} toggle={mToggle} size={mSize} class={mClass} backdrop="static">
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmBachiller">
					<div class="row g-3">
						<div class="col-12">
							<label for="id_titulo" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Título:</label
							>
							<FormSelectSearch
								inputId="id_titulo"
								name="titulo"
								bind:value={readSelectionTitulo}
								on:actionChangeSelectSearch={changeTitulo}
								disabled={bloqueo || mView}
								fetch={(query) => loadDataTitulos(query, 1)}
							/>
							<div class="valid-feedback" id="id_titulo_validate">¡Se ve bien!</div>
						</div>
						<div class="col-12">
							<label for="id_colegio" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Colegio / Unidad Educativa:</label
							>
							<FormSelectSearch
								inputId="id_colegio"
								name="colegio"
								bind:value={readSelectionColegio}
								on:actionChangeSelectSearch={changeColegio}
								disabled={bloqueo || mView}
								fetch={(query) => loadDataColegios(query)}
							/>
							<div class="valid-feedback" id="id_colegio_validate">¡Se ve bien!</div>
						</div>
						<div class="col-12 col-md-4">
							<label for="id_calificacion" class="form-label fw-bold">
								<span><i class="fe fe-alert-octagon text-warning" /></span> Calificación
							</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_calificacion"
								disabled={mView}
								use:cleave={{
									numeral: true,
									numeralDecimalMark: ',',
									numeralIntegerScale: 3,
									numeralDecimalScale: 0,
									numeralPositiveOnly: true,
									delimiter: '.'
								}}
								bind:value={inputCalificacion}
							/>
							<div class="valid-feedback" id="id_calificacion_validate">¡Se ve bien!</div>
						</div>
						<div class="col-12 col-md-4">
							<label for="id_anioinicioperiodograduacion" class="form-label fw-bold">
								<span><i class="fe fe-alert-octagon text-warning" /></span> Año de inicio
							</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_anioinicioperiodograduacion"
								disabled={mView}
								use:cleave={{
									date: true,
									dateMin: '1900',
									dateMax: '2099',
									datePattern: ['Y']
								}}
								bind:value={inputAnioInicio}
							/>
							<div class="valid-feedback" id="id_anioinicioperiodograduacion_validate">
								¡Se ve bien!
							</div>
						</div>
						<div class="col-12 col-md-4">
							<label for="id_aniofinperiodograduacion" class="form-label fw-bold">
								<span><i class="fe fe-alert-octagon text-warning" /></span> Año de graduación
							</label>
							<input
								type="text"
								class="form-control form-control-sm"
								id="id_aniofinperiodograduacion"
								disabled={bloqueo || mView}
								use:cleave={{
									date: true,
									dateMin: '1900',
									dateMax: '2099',
									datePattern: ['Y']
								}}
								bind:value={inputAnioFin}
							/>
							<div class="valid-feedback" id="id_aniofinperiodograduacion_validate">
								¡Se ve bien!
							</div>
						</div>
					</div>
					<hr />
					<h3 class="fw-bold text-primary">Archivos</h3>
					<div class="row g-3">
						<div class="col-md-6 col-12">
							<label for="id_actagrado" class="form-label fw-bold">Acta Grado:</label>
							{#if !mView}
								<FileUploader
									inputID="id_actagrado"
									inputName="actagrado"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedActaGrado}
									on:fileRemoved={handleFileRemovedActaGrado}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if download_actagrado != ''}
								<div class="fs-6">
									Tienes una acta de grado subido:
									<a
										title="Ver archivo"
										href={download_actagrado}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{:else if mView}
								<div class="fs-6">
									<p class="fw-bold text-danger">No tienes archivo subido de acta de grado</p>
								</div>
							{/if}

							<div class="valid-feedback" id="id_actagrado_validate">¡Se ve bien!</div>
						</div>

						<div class="col-md-6 col-12">
							<label for="id_reconocimientoacademico" class="form-label fw-bold"
								>Reconocimiento Académico:</label
							>
							{#if !mView}
								<FileUploader
									inputID="id_reconocimientoacademico"
									inputName="reconocimientoacademico"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedReconocimiento}
									on:fileRemoved={handleFileRemovedReconocimiento}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
							{/if}
							{#if download_reconocimientoacademico != ''}
								<div class="fs-6">
									Tienes un recocimiento académico subido:
									<a
										title="Ver archivo"
										href={download_reconocimientoacademico}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{:else if mView}
								<div class="fs-6">
									<p class="fw-bold text-danger">
										No tienes archivo subido de recocimiento académico
									</p>
								</div>
							{/if}

							<div class="valid-feedback" id="id_reconocimientoacademico_validate">
								¡Se ve bien!
							</div>
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
					<Button
						color="warning"
						class="rounded-5 btn-sm"
						on:click={saveFormacionAcademicaBachiller}><i class="fe fe-check" /> Guardar</Button
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
