<script lang="ts">
	import { apiPOST, apiPOSTFormData } from '$lib/utils/requestUtils';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { addToast } from '$lib/store/toastStore';
	import { loading } from '$lib/store/loadingStore';
	import FileUploader from '$components/Formulario/FileUploader.svelte';
	import { createEventDispatcher, onMount } from 'svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { customFormErrors } from '$lib/utils/forms';
	export let aData;
	export let mToggle;
	export let mTitle;
	export let mOpenModal;
	export let mClass;
	export let mSize;
	let eSolicitud;
	const dispatch = createEventDispatcher();

	let load = true;
	let mensaje_load = 'Cargando la información, espere por favor...';
	let inputDescripcion = '';
	let selectTipo = 0;
	let fileArchivo;
	let download_archivo = '';
	const eTipos = [{ id: 2, name: 'ACADÉMICA' }];
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eSolicitud = aData.eSolicitud;
		mensaje_load = 'Consultado la información, espere por favor...';
		await delay(1000);
		mensaje_load = 'Cargando la información, espere por favor...';
		if (eSolicitud) {
			selectTipo = eSolicitud.tipo ?? 0;
			inputDescripcion = eSolicitud.descripcion ?? '';
			if (eSolicitud.download_archivo) {
				download_archivo = eSolicitud.download_archivo;
			}
		}

		await delay(2000);
		load = false;
	});

	const saveSolicitudTutorSoporteMatricula = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmSolicitud = document.getElementById('frmSolicitud');
		const formData = new FormData($frmSolicitud);
		formData.append('tipo', selectTipo.toString());
		formData.append('descripcion', inputDescripcion);
		if (fileArchivo) {
			formData.append('archivo', fileArchivo.file);
		}
		if (eSolicitud != undefined) {
			formData.append('id', eSolicitud.pk ?? '0');
		} else {
			formData.append('id', '0');
		}
		formData.append('action', 'saveSolicitudTutorSoporteMatricula');
		//loading.setLoading(false, 'Guardando la información, espere por favor...');
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/solicitud_tutor/posgrado', formData);
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
				dispatch('actionRun', { action: 'saveSolicitudTutorSoporteMatricula' });
			}
		}
	};

	const handleFileSelectedArchivo = (event) => {
		fileArchivo = event.detail;
	};

	const handleFileRemovedArchivo = () => {
		fileArchivo = null;
	};
</script>

{#if mOpenModal}
	<Modal
		isOpen={true}
		toggle={mToggle}
		size={mSize}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
	>
		<ModalHeader toggle={mToggle} class="bg-primary text-white">
			<span class="text-white">{mTitle}</span>
		</ModalHeader>
		<ModalBody>
			{#if !load}
				<form action="javascript:;" id="frmSolicitud">
					<div class="row g-3">
						<div class="col-12 ">
							<label for="id_tipo" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Tipo:</label
							>
							<select
								class="form-select form-select-sm"
								aria-label=""
								id="id_tipo"
								bind:value={selectTipo}
							>
								<option value={0} selected> ----------- </option>
								{#each eTipos as eTipo}
									{#if selectTipo === eTipo.id}
										<option value={eTipo.id} selected>
											{eTipo.name}
										</option>
									{:else}
										<option value={eTipo.id}>
											{eTipo.name}
										</option>
									{/if}
								{/each}
							</select>

							<div class="valid-feedback" id="id_tipo_validate">¡Se ve bien!</div>
						</div>
						<div class="col-12 ">
							<label for="id_descripcion" class="form-label fw-bold"
								><span><i class="fe fe-alert-octagon text-warning" /></span> Descripcion de la solicitud:</label
							>
							<textarea
								id="id_descripcion"
								bind:value={inputDescripcion}
								class="form-control form-control-sm"
								rows="3"
							/>
							<div class="valid-feedback" id="id_descripcion_validate">¡Se ve bien!</div>
						</div>

						<div class="col-12">
							<label for="id_archivo" class="form-label fw-bold">Archivo:</label>
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
				<Button
					color="warning"
					class="rounded-5 btn-sm"
					on:click={saveSolicitudTutorSoporteMatricula}><i class="fe fe-check" /> Guardar</Button
				>
			{/if}
			<Button color="secondary" class="rounded-5 btn-sm " on:click={mToggle}
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
