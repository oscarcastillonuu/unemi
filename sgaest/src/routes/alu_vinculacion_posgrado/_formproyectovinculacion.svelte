<script lang="ts">
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { onMount } from 'svelte';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import { loading } from '$lib/store/loadingStore';
	//import Input from '$components/Forms/Input.svelte'
	import { addNotification } from '$lib/store/notificationStore';
	import { goto } from '$app/navigation';
	import { createEventDispatcher, onDestroy } from 'svelte';

	import Select from 'svelte-select';

	const dispatch = createEventDispatcher();

	export let aData;
	export let toggle;
	export let mOpen;
	let id = null;
	let titulo = '';
	let descripcion = '';
	let eTipoevidencia = [];
	let tipoevidencia_id = '';
	let pondEvidencia;
	let nameEvidencia = 'fileEvidencia';
	let url = '';
	let archivo = '';
	let ocultar = false;
	let proyecto_vinvulacion = {};
	let participanteproyectov = {};
	let files = [];
	let idParticipanteProyectoVinculacion = '';

	onMount(async () => {
		console.log(aData);
		eTipoevidencia = aData.tipo_evidencia;
		if (aData.participanteproyectov) {
			participanteproyectov = aData.participanteproyectov;
			proyecto_vinvulacion = aData.participanteproyectov.proyectovinculacion;
			idParticipanteProyectoVinculacion = participanteproyectov.id;
			titulo = proyecto_vinvulacion.titulo;
			descripcion = proyecto_vinvulacion.descripcion;
			tipoevidencia_id = participanteproyectov.tipoevidencia;

			if (tipoevidencia_id == 1) {
				archivo = participanteproyectov.download_link;
			}

			if (tipoevidencia_id == 2) {
				url = participanteproyectov.download_link
			}


		}
	});

	// handle filepond events
	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondEvidencia.getFiles());
		console.log('A file has been added', fileItem);
	};


	const savefrmProyectovin = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmProyectovin = document.querySelector('#frmProyectovin');
		const formData = new FormData($frmProyectovin);
		formData.append('action', idParticipanteProyectoVinculacion ? 'update_proyecto_vinculacion' : 'save_proyecto_vinculacion');
		formData.append('id', idParticipanteProyectoVinculacion);
		formData.append('tipo_evidencia_id', tipoevidencia_id);

		if (tipoevidencia_id == 1) {

			let fileDocumento = pondEvidencia.getFiles();
			if (fileDocumento.length == 0) {
				if (archivo === ''){
					addNotification({
						msg: 'Debe subir un archivo',
						type: 'error',
						target: 'newNotificationToast'
					});
					loading.setLoading(false, 'Cargando, espere por favor...');
					return;
				}
			}
			if (fileDocumento.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}

			let eFileDocumento = undefined;
			if (fileDocumento.length > 0) {
				eFileDocumento = fileDocumento[0];
				formData.append('fileDocumento', eFileDocumento.file);
			}else{
				if (archivo !== '') {
				formData.append('archivo', archivo);
				}
			}

		}

		for (const [key, value] of formData.entries()) {
			console.log(`${key}: ${value}`);
		}

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/alu_vinculacion_posgrado', formData);

		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				loading.setLoading(false, 'Cargando, espere por favor...');
				toggle();
				dispatch('saveproyectovinculacion');
			}
		}
	};
</script>

<form
	id="frmProyectovin"
	enctype="multipart/form-data"
	on:submit|preventDefault={savefrmProyectovin}
>
	<div class="card-body">
		<div class="row">
			<div class="col-12 rowinput">
				<div class="form-group">
					<label for="titulo" class="form-label fw-bold">
						<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" />
						Título:
					</label>
					<textarea
						type="text"
						class="form-control"
						id="titulo"
						bind:value={titulo}
						name="titulo"
						required
					/>
				</div>
			</div>

			<div class="col-12 rowinput">
				<label for="descripcion" class="form-label fw-bold">
					<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" />
					Descripcion:
				</label>
				<textarea
					type="text"
					class="form-control"
					id="descripcion"
					name="descripcion"
					cols="30"
					rows="2"
					bind:value={descripcion}
					required
				/>
			</div>

			<div class="col-12 rowinput">
				<label for="eTipoEvidencia" class="form-label fw-bold">
					<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" />
					Tipo de evidencia:
				</label>

				<Select
					id="eTipoEvidencia"
					placeholder="Seleccione..."
					items={eTipoevidencia}
					itemId="id"
					label="nombre"
					bind:justValue={tipoevidencia_id}
					value={eTipoevidencia.find((x) => x.id === tipoevidencia_id)}
					class="form-control form-select"
					style="width: 100%"
					required
				/>
			</div>

			{#if tipoevidencia_id == 1}
				<div class="col-12 rowinput">
					<label for="eEvidenciaFileDocumento" class="form-label fw-bold">
						<i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red" />
						Evidencia:
					</label>
					<FilePond
						id="eEvidenciaFileDocumento"
						class="pb-0 mb-0"
						bind:this={pondEvidencia}
						{nameEvidencia}
						name="fileDocumento"
						labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
						allowMultiple={true}
						oninit={handleInit}
						onaddfile={handleAddFile}
						credits=""
						acceptedFileTypes={['application/pdf']}
						labelInvalidField="El campo contiene archivos no válidos"
						maxFiles="1"
						maxParallelUploads="1"
					/>
					<br />
					<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small><br />
					{#if archivo !== ''}
								<div class="fs-6">
									Tienes un archivo subido:
									<a
										title="Ver archivo"
										href={archivo}
										target="_blank"
										class="text-primary text-center">Ver archivo</a
									>
								</div>
							{/if}
				</div>
			{/if}

			{#if tipoevidencia_id == 2}
				<div class="col-12 rowinput">
					<div class="form-group">
						<label for="url" class="form-label fw-bold">
							<i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/>
							Url:
						</label>
						<input type="text" class="form-control" id="url" bind:value={url} name="url" required />
					</div>
				</div>
			{/if}
		</div>
	</div>
	<div class="card-footer text-muted">
		<div class="d-grid gap-2 d-md-flex justify-content-md-end">
			{#if !ocultar}
				<button type="submit" class="btn btn-info">Guardar</button>
			{/if}
			<a
				color="danger"
				class="btn  {ocultar ? 'btn-info' : 'btn-danger '}"
				on:click={() => toggle()}
			>
				{#if ocultar}Cerrar{:else}Cancelar{/if}
			</a>
		</div>
	</div>
</form>

<style>
	@import 'filepond/dist/filepond.css';

	.rowinput {
		margin-bottom: 1.5rem;
	}
</style>
