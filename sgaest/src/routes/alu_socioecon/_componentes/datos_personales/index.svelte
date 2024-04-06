<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponentEdit from './edit.svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	let mOpenModal = false;
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let ePersona = {};
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePersona = aData.ePersona ?? {};
		}
	});

	const dispatch = createEventDispatcher();
	
	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (action == 'saveDatosPersonales') {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_1');
			menu.click();
		}
	};

	const openModalEdit = () => {
		modalDetalleContent = ComponentEdit;
		mOpenModal = !mOpenModal;
		// modalTitle = 'Actualizar datos personales';
		aDataModal = { ePersona: ePersona };
	};
</script>

<div class="card border-0">
	<div class="card-header d-lg-flex justify-content-between align-items-center">
		<div class="mb-3 mb-lg-0">
			<h3 class="mb-0">Datos personales</h3>
			<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
		</div>
		<div>
			<button class="btn btn-success btn-sm" on:click={() => openModalEdit()}>Editar</button>
		</div>
	</div>
	<div class="card-body">
		<div class="d-lg-flex align-items-center justify-content-between">
			<div class="d-flex align-items-center mb-4 mb-lg-0">
				<img
					src={ePersona.foto_perfil}
					id="img-uploaded"
					class="avatar-xl rounded-circle"
					alt="avatar"
				/>
				<div class="ms-3">
					<h4 class="mb-0">Tu foto de perfil</h4>
					<p class="mb-0">Tamaño máximo permitido 15Mb, en formato jpg</p>
				</div>
			</div>
			<div>
				<a href="/changepicture" class="btn btn-outline-secondary btn-sm">Actualizar foto</a>
				<!--<button class="btn btn-outline-danger btn-sm">Eliminar</button>-->
			</div>
		</div>
		<hr class="my-5" />
		<div>
			<div class="row mb-4">
				<div class="col-lg-3 col-md-3 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Nombres:</span>
					<h6 class="mb-0">{ePersona.nombres}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">1er. Apellido:</span>
					<h6 class="mb-0">{ePersona.apellido1}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">2do. Apellido:</span>
					<h6 class="mb-0">{ePersona.apellido2}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Fecha de nacimiento:</span>
					<h6 class="mb-0">{ePersona.nacimiento}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Tipo de documento:</span>
					<h6 class="mb-0">{ePersona.tipo_documento}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Documento:</span>
					<h6 class="mb-0">
						{ePersona.documento}
					</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Nacionalidad:</span>
					<h6 class="mb-0">{ePersona.nacionalidad}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Estado civil:</span>
					<h6 class="mb-0">{ePersona.estado_civil ? ePersona.estado_civil.nombre : 'S/N'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Sexo:</span>
					<h6 class="mb-0">{ePersona.sexo ? ePersona.sexo.nombre : 'S/N'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">¿Pertenece al Grupo LGTBI?</span>
					<h6 class="mb-0">
						{#if ePersona.lgtbi}
							<span class="badge bg-success"> SI</span>
						{:else}
							<span class="badge bg-danger"> NO</span>
						{/if}
					</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Libreta militar:</span>
					<h6 class="mb-0">
						{ePersona.libretamilitar ? ePersona.libretamilitar : 'S/N'}
					</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Correo electrónico:</span>
					<h6 class="mb-0">{ePersona.email ? ePersona.email : 'S/N'}</h6>
				</div>
			</div>
		</div>
		<hr class="my-5" />
		<div class="table-responsive border-0 overflow-y-hidden">
			<table class="table mb-0 text-nowrap table-hover table-centered">
				<thead>
					<tr>
						<th class="text-center">Archivo</th>
						<th class="text-center">Tipo</th>
						<th class="text-center">Estado</th>
					</tr>
				</thead>
				<tbody>
					{#if ePersona.download_documento}
						<tr>
							<td class="text-center">
								<a
									href={ePersona.download_documento}
									target="_blank"
									class="btn btn-primary btn-sm rounded-pill text-white"
								>
									<p class="m-0 p-0">
										Ver archivo
										<i class="bi bi-download" />
									</p>
								</a>
							</td>
							<td class="text-center"> {ePersona.tipo_documento} </td>
							<td class="text-center">
								{#if ePersona.estadodocumento_display === 'VALIDADO'}
									<span class="badge bg-success">VALIDADO</span>
								{:else if ePersona.estadodocumento_display === 'RECHAZADO'}
									<span class="badge bg-danger">RECHAZADO</span>
								{:else}
									<span class="badge bg-info">CARGADO</span>
								{/if}
							</td>
						</tr>
					{/if}
					{#if ePersona.download_papeleta}
						<tr>
							<td class="text-center">
								<a
									href={ePersona.download_papeleta}
									target="_blank"
									class="btn btn-primary btn-sm rounded-pill text-white"
								>
									<p class="m-0 p-0">
										Ver archivo
										<i class="bi bi-download" />
									</p>
								</a>
							</td>
							<td class="text-center"> CERTIFICADO DE VOTACIÓN </td>
							<td class="text-center">
								{#if ePersona.estadopapeleta_display === 'VALIDADO'}
									<span class="badge bg-success">VALIDADO</span>
								{:else if ePersona.estadopapeleta_display === 'RECHAZADO'}
									<span class="badge bg-danger">RECHAZADO</span>
								{:else}
									<span class="badge bg-info">CARGADO</span>
								{/if}
							</td>
						</tr>
					{/if}
					{#if ePersona.download_libretamilitar}
						<tr>
							<td class="text-center">
								<a
									href={ePersona.download_libretamilitar}
									target="_blank"
									class="btn btn-primary btn-sm rounded-pill text-white"
								>
									<p class="m-0 p-0">
										Ver archivo
										<i class="bi bi-download" />
									</p>
								</a>
							</td>
							<td class="text-center"> LIBRETA MILITAR </td>
							<td class="text-center">
								{#if ePersona.estadolibretamilitar_display === 'VALIDADO'}
									<span class="badge bg-success">VALIDADO</span>
								{:else if ePersona.estadolibretamilitar_display === 'RECHAZADO'}
									<span class="badge bg-danger">RECHAZADO</span>
								{:else}
									<span class="badge bg-info">CARGADO</span>
								{/if}
							</td>
						</tr>
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>

{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		mToggle={mToggleModal}
		on:actionRun={actionRun}
	/>
{/if}
