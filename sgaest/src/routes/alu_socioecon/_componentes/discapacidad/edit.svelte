<script lang="ts">
	import { apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import {
		getInstitucionesDiscapacidad as loadInstituciones,
		getDiscapacidades as loadDiscapacidades
	} from '$lib/utils/loadDataApi';
	import { customFormErrors } from '$lib/utils/forms';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import FormSelect from '$components/Formulario/Select.svelte';
	import FormMultiselect from '$components/Formulario/Multiselect.svelte';
	export let aData;
	export let mToggle;
	let ePerfilInscripcion;
	let eInstituciones;
	let eDiscapacidades;
	const dispatch = createEventDispatcher();
	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputTieneDiscapacidad = false;
	let selectDiscapacidad = 0;
	let selectGrado = 0;
	let selectInstitucion = 0;
	let valueInstitucion = undefined;
	let inputCarnet = '';
	let inputPorciento = 0;
	let selectDiscapacidadMultiples = [];
	let valueDiscapacidadMultiples = [];
	let fileDiscapacidad;
	let download_archivo = '';
	let inputTieneDiscapacidadMultiple = false;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let Grados = [
		{ value: 0, label: `NO DETERMINADO` },
		{ value: 1, label: `LEVE` },
		{ value: 2, label: `MODERADO` },
		{ value: 3, label: `GRAVE` }
	];
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		ePerfilInscripcion = aData.ePerfilInscripcion;
		mensaje_load = 'Consultado la información, espere por favor...';
		eDiscapacidades = await loadDiscapacidades();
		eInstituciones = await loadInstituciones();
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		inputTieneDiscapacidad = ePerfilInscripcion.tienediscapacidad;
		if (ePerfilInscripcion.tipodiscapacidad) {
			selectDiscapacidad = ePerfilInscripcion.tipodiscapacidad['pk'] ?? 0;
		}
		selectGrado = ePerfilInscripcion.grado;
		if (ePerfilInscripcion.institucionvalida) {
			selectInstitucion = ePerfilInscripcion.institucionvalida['pk'] ?? 0;
			valueInstitucion = {
				id: ePerfilInscripcion.institucionvalida['pk'],
				name: ePerfilInscripcion.institucionvalida['nombre']
			};
		}
		inputCarnet = ePerfilInscripcion.carnetdiscapacidad;
		inputPorciento = ePerfilInscripcion.porcientodiscapacidad ?? 0;
		if (ePerfilInscripcion.download_archivo) {
			download_archivo = ePerfilInscripcion.download_archivo;
		}
		inputTieneDiscapacidadMultiple = ePerfilInscripcion.tienediscapacidadmultiple;
		if (ePerfilInscripcion.tipodiscapacidadmultiple.length) {
			let ids_multiples = [];
			ePerfilInscripcion.tipodiscapacidadmultiple.forEach((discapacidad) => {
				valueDiscapacidadMultiples.push({
					id: discapacidad['pk'],
					name: discapacidad['nombre']
				});
				ids_multiples.push(discapacidad['pk']);
			});
			selectDiscapacidadMultiples = ids_multiples;
		}
		await delay(2000);
		load = false;
	});

	const saveDatosDiscapacidad = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmDatosDiscapacidad = document.getElementById('frmDatosDiscapacidad');
		const formData = new FormData($frmDatosDiscapacidad);
		//const numeros = /^([0-9])*$/;
		formData.append('tienediscapacidad', inputTieneDiscapacidad ? 'true' : 'false');
		if (selectDiscapacidad != 0) {
			formData.append('tipodiscapacidad', selectDiscapacidad.toString());
		}

		formData.append('grado', selectGrado.toString());
		formData.append('carnetdiscapacidad', inputCarnet);
		formData.append('porcientodiscapacidad', inputPorciento.toString());
		if (selectInstitucion != undefined) {
			formData.append('institucionvalida', selectInstitucion.toString());
		}

		if (fileDiscapacidad) {
			formData.append('archivo', fileDiscapacidad.file);
		}
		formData.append('tienediscapacidadmultiple', inputTieneDiscapacidadMultiple ? 'true' : 'false');
		if (selectDiscapacidadMultiples != null) {
			let ids = [];
			selectDiscapacidadMultiples.forEach(element => {
				ids.push(element);
			});
			formData.append('tipodiscapacidadmultiple', JSON.stringify(ids));
		}

		formData.append('action', 'saveDatosDiscapacidad');
		//console.log(selectDiscapacidadMultiples);
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/socioeconomica', formData);
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
				dispatch('actionRun', { action: 'saveDatosDiscapacidad' });
			}
		}
	};

	const handleFileSelectedDiscapacidad = (event) => {
		fileDiscapacidad = event.detail;
	};

	const handleFileRemovedDiscapacidad = () => {
		fileDiscapacidad = null;
	};
</script>

{#if ePerfilInscripcion}
	<Modal
		id="modal_edit_discapacidad"
		isOpen={true}
		toggle={mToggle}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">Actualizar datos de discapacidad</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmDatosDiscapacidad">
					<div class="row g-3">
						<div class="col-md-12 col-lg-12 col-sm-12">
							<div class="form-check form-switch">
								<input
									class="form-check-input"
									type="checkbox"
									id="id_tienediscapacidad"
									bind:checked={inputTieneDiscapacidad}
								/>
								<label class="form-check-label fw-bold text-dark" for="id_tienediscapacidad"
									>¿Tienes discapacidad?</label
								>
							</div>
							<div class="valid-feedback" id="id_tienediscapacidad_validate">¡Se ve bien!</div>
						</div>
						{#if inputTieneDiscapacidad}
							<div class="col-md-6 col-lg-6 col-sm-12">
								<label for="id_tipodiscapacidad" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Tipo de discapacidad:</label
								>
								{#if eDiscapacidades}
									<select
										class="form-select form-select-sm"
										aria-label=""
										required
										id="id_tipodiscapacidad"
										bind:value={selectDiscapacidad}
									>
										<option value={0} selected> ----------- </option>
										{#each eDiscapacidades as eDiscapacidad}
											{#if selectDiscapacidad === eDiscapacidad.id}
												<option value={eDiscapacidad.id} selected>
													{eDiscapacidad.name}
												</option>
											{:else}
												<option value={eDiscapacidad.id}>
													{eDiscapacidad.name}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
								<div class="valid-feedback" id="id_tipodiscapacidad_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-6 col-lg-6 col-sm-12">
								<label for="id_grado" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Grado de discapacidad:</label
								>
								{#if Grados}
									<select
										class="form-select form-select-sm"
										aria-label=""
										required
										id="id_grado"
										bind:value={selectGrado}
									>
										{#each Grados as Grado}
											{#if selectGrado === Grado.value}
												<option value={Grado.value} selected>
													{Grado.label}
												</option>
											{:else}
												<option value={Grado.value}>
													{Grado.label}
												</option>
											{/if}
										{/each}
									</select>
								{/if}
								<div class="valid-feedback" id="id_grado_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-6 col-lg-6 col-sm-12">
								<label for="id_carnetdiscapacidad" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Nro carné:</label
								>
								<input
									type="text"
									class="form-control form-control-sm"
									id="id_carnetdiscapacidad"
									bind:value={inputCarnet}
								/>
								<div class="valid-feedback" id="id_carnetdiscapacidad_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-6 col-lg-6 col-sm-12">
								<label for="id_porcientodiscapacidad" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Porcentaje:</label
								>
								<input
									type="text"
									class="form-control form-control-sm"
									id="id_porcientodiscapacidad"
									bind:value={inputPorciento}
								/>
								<div class="valid-feedback" id="id_porcientodiscapacidad_validate">
									¡Se ve bien!
								</div>
							</div>
							<div class="col-md-12 col-lg-12 col-sm-12">
								<label for="id_institucionvalida" class="form-label fw-bold"
									><span><i class="fe fe-alert-octagon text-warning" /></span> Institución valida:</label
								>
								{#if eInstituciones}
									<FormSelect
										id="id_institucionvalida"
										name="institucionvalida"
										clases="form-control form-control-sm"
										itemId="id"
										label="name"
										items={eInstituciones}
										value={valueInstitucion}
										bind:justValue={selectInstitucion}
									/>									
								{/if}
								<div class="valid-feedback" id="id_institucionvalida_validate">¡Se ve bien!</div>
							</div>
							<div class="col-md-12 col-lg-12 col-sm-12">
								<label for="id_archivo" class="form-label fw-bold">Archivo del carné:</label>
								<FileUploader
									inputID="id_archivo"
									inputName="archivo"
									acceptedFileTypes={['application/pdf']}
									labelFileTypeNotAllowedMessage={'Solo se permiten archivos PDF'}
									on:fileSelected={handleFileSelectedDiscapacidad}
									on:fileRemoved={handleFileRemovedDiscapacidad}
								/>
								<div class="text-center fs-6">
									<small class="text-warning ">Tamaño máximo permitido 15Mb, en formato pdf</small>
								</div>
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
								{/if}

								<div class="valid-feedback" id="id_archivo_validate">¡Se ve bien!</div>
							</div>
							<hr />

							<div class="col-md-12 col-lg-12 col-sm-12">
								<div class="form-check form-switch">
									<input
										class="form-check-input"
										type="checkbox"
										id="id_tienediscapacidadmultiple"
										bind:checked={inputTieneDiscapacidadMultiple}
									/>
									<label
										class="form-check-label fw-bold text-dark"
										for="id_tienediscapacidadmultiple">¿Tiene Discapacidad multiple?</label
									>
								</div>
								<div class="valid-feedback" id="id_tienediscapacidadmultiple_validate">
									¡Se ve bien!
								</div>
							</div>
							{#if inputTieneDiscapacidadMultiple}
								<div class="col-md-12 col-lg-12 col-sm-12">
									<label for="id_tipodiscapacidadmultiple" class="form-label fw-bold"
										><span><i class="fe fe-alert-octagon text-warning" /></span> Institución valida:</label
									>
									{#if eDiscapacidades}
										<FormMultiselect
											id="id_tipodiscapacidadmultiple"
											name="tipodiscapacidadmultiple"
											clases="form-control form-control-sm"
											itemId="id"
											label="name"
											items={eDiscapacidades}
											value={valueDiscapacidadMultiples}
											bind:justValue={selectDiscapacidadMultiples}
										/>
									{/if}
									<div class="valid-feedback" id="id_tipodiscapacidadmultiple_validate">
										¡Se ve bien!
									</div>
								</div>
							{/if}
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
			<Button color="secondary" class="rounded-3 btn-sm" on:click={mToggle}>Cerrar</Button>
			{#if !load}
				<Button color="primary" class="rounded-3 btn-sm" on:click={saveDatosDiscapacidad}
					>Guardar</Button
				>
			{/if}
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
