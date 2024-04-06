<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponentFrmDatosPersonales from './frmDatosPersonales.svelte';
	import ComponentFrmDatosNacimiento from './frmDatosNacimiento.svelte';
	import ComponentFrmDatosDomicilio from './frmDatosDomicilio.svelte';
	import { Button, Modal, ModalBody, ModalFooter, ModalHeader, Tooltip } from 'sveltestrap';
	import { navigating } from '$app/stores';
	import { loading } from '$lib/store/loadingStore';
	import ComponentViewPDF from '$components/viewPDF.svelte';
	let mOpenModal = false;
	let mTitleModal;
	let mClassModal =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
	let mSizeModal = 'lg';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	let modalDetalleContent;
	export let aData;
	let aDataModal;
	let ePersona = {};
	let eNacionalidad;
	let ePaisNacimiento;
	let eProvinciaNacimiento;
	let eCantonNacimiento;
	let eParroquiaNacimiento;
	let ePais;
	let eProvincia;
	let eCanton;
	let eParroquia;
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	onMount(async () => {
		if (aData) {
			ePersona = aData.ePersona ?? {};
			console.log(ePersona);
			if (ePersona.paisnacionlidad) {
				eNacionalidad = { ...ePersona.paisnacionlidad };
			}
			if (ePersona.paisnacimiento) {
				ePaisNacimiento = { ...ePersona.paisnacimiento };
			}
			if (ePersona.provincianacimiento) {
				eProvinciaNacimiento = { ...ePersona.provincianacimiento };
			}
			if (ePersona.cantonnacimiento) {
				eCantonNacimiento = { ...ePersona.cantonnacimiento };
			}
			if (ePersona.parroquianacimiento) {
				eParroquiaNacimiento = { ...ePersona.parroquianacimiento };
			}
			if (ePersona.paisnacionalidad) {
				eNacionalidad = { ...ePersona.paisnacionalidad };
			}
			if (ePersona.pais) {
				ePais = { ...ePersona.pais };
			}
			if (ePersona.provincia) {
				eProvincia = { ...ePersona.provincia };
			}
			if (ePersona.canton) {
				eCanton = { ...ePersona.canton };
			}
			if (ePersona.parroquia) {
				eParroquia = { ...ePersona.parroquia };
			}
		}
	});

	const dispatch = createEventDispatcher();

	const actionRun = (event) => {
		const detail = event.detail;
		const action = detail.action;
		if (
			action == 'saveDatosPersonalesBasico' ||
			action == 'saveDatosPersonalesNacimiento' ||
			action == 'saveDatosPersonalesDomicilio'
		) {
			mOpenModal = !mOpenModal;
			const menu = document.getElementById('menu_element_1');
			menu.click();
		}
	};

	const openModalEdit = (component, title) => {
		modalDetalleContent = component;
		mOpenModal = !mOpenModal;
		mTitleModal = title;
		aDataModal = { ePersona: ePersona };
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'lg';
	};

	const view_pdf = (url) => {
		aDataModal = { url: url };
		modalDetalleContent = ComponentViewPDF;
		mOpenModal = !mOpenModal;
		mTitleModal = 'Ver pdf';
		mClassModal =
			'modal-dialog modal-dialog-centered modal-dialog-scrollable  modal-fullscreen-lg-down';
		mSizeModal = 'xl';
	};
</script>

{#if ePersona}
	<div class="card border-0">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Datos personales</h3>
				<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
			</div>
			<div>
				<button
					class="btn btn-success btn-sm btn-cian-opacity"
					on:click={() => openModalEdit(ComponentFrmDatosPersonales, 'Editar datos personales')}
					><i class="fe fe-edit " /> Editar</button
				>
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
					<a href="/changepicture" class="btn btn-outline-warning btn-sm">Actualizar foto</a>
					<!--<button class="btn btn-outline-danger btn-sm">Eliminar</button>-->
				</div>
			</div>
			<hr class="my-5" />
			<div class="row">
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
					<span class="fs-6">Pais de nacionalidad:</span>
					{#if eNacionalidad}
						<h6 class="mb-0">{eNacionalidad.nombre}</h6>
					{:else}
						<h6 class="mb-0">S/N</h6>
					{/if}
				</div>

				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">{ePersona.tipo_documento}:</span>
					<h6 class="mb-0">
						{ePersona.documento}
						{#if ePersona.download_documento}
							<a
								href="javascript:;"
								class=""
								on:click={() => view_pdf(ePersona.download_documento)}
								id="Tooltip_documento"
							>
								<i class="bi bi-eye text-warning" />
							</a>

							<Tooltip target="Tooltip_documento" placement="top"
								>Visualizar {ePersona.tipo_documento}</Tooltip
							>
							{#if ePersona.estadodocumento_display === 'VALIDADO'}
								<span class="badge-dot bg-success" id="Tooltip_documento_estado">VALIDADO</span>
							{:else if ePersona.estadodocumento_display === 'RECHAZADO'}
								<span class="badge-dot bg-danger" id="Tooltip_documento_estado">RECHAZADO</span>
							{:else}
								<span class="badge-dot bg-secondary" id="Tooltip_documento_estado">CARGADO</span>
							{/if}
							<Tooltip target="Tooltip_documento_estado" placement="top"
								>Estado de archivo: {ePersona.estadodocumento_display}</Tooltip
							>
						{/if}
					</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Fecha de nacimiento:</span>
					<h6 class="mb-0">{ePersona.nacimiento}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Estado civil:</span>
					<h6 class="mb-0">{ePersona.estado_civil ? ePersona.estado_civil.nombre : 'S/N'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Género:</span>
					<h6 class="mb-0">{ePersona.sexo ? ePersona.sexo.nombre : 'S/N'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Grupo LGTBI:</span>
					<h6 class="mb-0">{ePersona.lgtbi ? 'SI' : 'NO'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Certificado de votación:</span>

					{#if ePersona.download_papeleta}
						<a
							href="javascript:;"
							class=""
							on:click={() => view_pdf(ePersona.download_papeleta)}
							id="Tooltip_votacion"
						>
							<i class="bi bi-eye text-warning" />
						</a>

						<Tooltip target="Tooltip_votacion" placement="top"
							>Visualizar certificado de votación</Tooltip
						>
					{/if}
					<h6 class="mb-0">
						{ePersona.estadopapeleta_display}
					</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Libreta militar:</span>
					<h6 class="mb-0">
						{ePersona.libretamilitar ? ePersona.libretamilitar : 'S/N'}
						{#if ePersona.download_libretamilitar}
							<a
								href="javascript:;"
								class=""
								on:click={() => view_pdf(ePersona.download_libretamilitar)}
								id="Tooltip_libreta_militar"
							>
								<i class="bi bi-eye text-warning" />
							</a>

							<Tooltip target="Tooltip_libreta_militar" placement="top"
								>Visualizar libreta militar</Tooltip
							>
							{#if ePersona.estadolibretamilitar_display === 'VALIDADO'}
								<span class="badge-dot bg-success" id="Tooltip_militar_estado">VALIDADO</span>
							{:else if ePersona.estadolibretamilitar_display === 'RECHAZADO'}
								<span class="badge-dot bg-danger" id="Tooltip_militar_estado">RECHAZADO</span>
							{:else}
								<span class="badge-dot bg-secondary" id="Tooltip_militar_estado">CARGADO</span>
							{/if}
							<Tooltip target="Tooltip_militar_estado" placement="top"
								>Estado de archivo: {ePersona.estadolibretamilitar_display}</Tooltip
							>
						{/if}
					</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Correo electrónico institucional:</span>
					<h6 class="mb-0">{ePersona.emailinst ? ePersona.emailinst : 'S/N'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Correo electrónico personal:</span>
					<h6 class="mb-0">{ePersona.email ? ePersona.email : 'S/N'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Persona zurda:</span>
					<h6 class="mb-0">{ePersona.eszurdo ? 'SI' : 'NO'}</h6>
				</div>
				<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Discapacidad:</span>
					<h6 class="mb-0">{ePersona.tiene_discapasidad ? 'SI' : 'NO'}</h6>
				</div>
				{#if ePersona.raza}
					<div class="col-lg-3 col-md-4 col-sm-6 col-12 mb-2 mb-lg-2">
						<span class="fs-6">Etnia/Pueblo:</span>
						<h6 class="mb-0">{ePersona.raza}</h6>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="card border-0 mt-5">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Datos de nacimiento</h3>
				<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
			</div>
			<div>
				<button
					class="btn btn-success btn-sm btn-cian-opacity"
					on:click={() => openModalEdit(ComponentFrmDatosNacimiento, 'Editar datos de nacimiento')}
					><i class="fe fe-edit " /> Editar</button
				>
			</div>
		</div>

		<div class="card-body">
			<div class="row">
				{#if ePaisNacimiento}
					<div class="col-lg-3 col-md-6 col-12 mb-2 mb-lg-2">
						<!-- Custom Switch -->
						<span class="fs-6">Pais:</span>
						<h6 class="mb-0">{ePaisNacimiento.nombre}</h6>
					</div>
				{/if}
				{#if eProvinciaNacimiento}
					<div class="col-lg-3 col-md-6 col-12 mb-2 mb-lg-2">
						<!-- Custom Switch -->
						<span class="fs-6">Provincia:</span>
						<h6 class="mb-0">{eProvinciaNacimiento.nombre}</h6>
					</div>
				{/if}
				{#if eCantonNacimiento}
					<div class="col-lg-3 col-md-6 col-12 mb-2 mb-lg-2">
						<!-- Custom Switch -->
						<span class="fs-6">Cantón:</span>
						<h6 class="mb-0">{eCantonNacimiento.nombre}</h6>
					</div>
				{/if}
				{#if eParroquiaNacimiento}
					<div class="col-lg-3 col-md-6 col-12 mb-2 mb-lg-2">
						<!-- Custom Switch -->
						<span class="fs-6">Parroquia:</span>
						<h6 class="mb-0">{eParroquiaNacimiento.nombre}</h6>
					</div>
				{/if}
			</div>
		</div>
	</div>

	<div class="card border-0 mt-5">
		<div class="card-header d-sm-flex justify-content-between align-items-center">
			<div class="headtitle  mb-lg-0 m-0">
				<h3 class="mx-2 m-0 p-0">Datos de domicilio</h3>
				<!--<p class="mb-0">Here is list of package/product that you have subscribed.</p>-->
			</div>
			<div>
				<button
					class="btn btn-success btn-sm btn-cian-opacity"
					on:click={() => openModalEdit(ComponentFrmDatosDomicilio, 'Editar datos de domicilio')}
					><i class="fe fe-edit " /> Editar</button
				>
			</div>
		</div>

		<div class="card-body">
			<div class="row">
				{#if ePais}
					<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
						<span class="fs-6">Pais de residencia:</span>
						<h6 class="mb-0">{ePais.nombre}</h6>
					</div>
				{/if}
				{#if eProvincia}
					<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
						<span class="fs-6">Provincia de residencia:</span>
						<h6 class="mb-0">{eProvincia.nombre}</h6>
					</div>
				{/if}
				{#if eCanton}
					<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
						<span class="fs-6">Cantón de residencia: </span>
						<h6 class="mb-0">{eCanton.nombre}</h6>
					</div>
				{/if}
				{#if eParroquia}
					<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
						<span class="fs-6">Parroquia de residencia:</span>
						<h6 class="mb-0">{eParroquia.nombre}</h6>
					</div>
				{/if}
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Calle principal:</span>
					<h6 class="mb-0">{ePersona.direccion ?? 'S/D'}</h6>
				</div>

				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Calle secundaria:</span>
					<h6 class="mb-0">{ePersona.direccion2 ?? 'S/D'}</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Ciudadela:</span>
					<h6 class="mb-0">{ePersona.ciudadela ?? 'S/C'}</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Número de casa:</span>
					<h6 class="mb-0">{ePersona.num_direccion ?? 'S/N'}</h6>
				</div>

				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Referencia:</span>
					<h6 class="mb-0 text-truncate">{ePersona.referencia ?? 'S/R'}</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Teléfono domicilio (fijo):</span>
					<h6 class="mb-0">{ePersona.telefono_conv ?? 'S/T'}</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Celular:</span>
					<h6 class="mb-0">
						{ePersona.telefono ?? 'S/T'}
					</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Sector:</span>
					<h6 class="mb-0">{ePersona.sector ?? 'S/S'}</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					<span class="fs-6">Zona residencial:</span>
					<h6 class="mb-0">{ePersona.zona_display ?? 'S/Z'}</h6>
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					{#if ePersona.download_planilla_luz}
						<span class="fs-6">
							Planilla de luz:
							<a
								href="javascript:;"
								class=""
								on:click={() => view_pdf(ePersona.download_planilla_luz)}
								id="Tooltip_planilla_luz"
							>
								<i class="bi bi-eye text-warning" />
							</a>

							<Tooltip target="Tooltip_planilla_luz" placement="top"
								>Visualizar planilla de luz</Tooltip
							>
						</span>
					{:else}
						<span class="fs-6"> Planilla de luz: </span>
						<h6 class="mb-0">S/C</h6>
					{/if}
				</div>
				<div class="col-lg-3 col-md-3 col-12 mb-2 mb-lg-2">
					{#if ePersona.download_croquis}
						<span class="fs-6">
							Croquis:
							<a
								href="javascript:;"
								class=""
								on:click={() => view_pdf(ePersona.download_croquis)}
								id="Tooltip_croquis"
							>
								<i class="bi bi-eye text-warning" />
							</a>

							<Tooltip target="Tooltip_croquis" placement="top">Visualizar croquis</Tooltip>
						</span>
					{:else}
						<span class="fs-6"> Croquis: </span>
						<h6 class="mb-0">S/C</h6>
					{/if}
				</div>
			</div>
		</div>
	</div>
{/if}
{#if mOpenModal}
	<svelte:component
		this={modalDetalleContent}
		aData={aDataModal}
		{mOpenModal}
		mToggle={mToggleModal}
		mTitle={mTitleModal}
		mClass={mClassModal}
		mSize={mSizeModal}
		on:actionRun={actionRun}
	/>
{/if}
