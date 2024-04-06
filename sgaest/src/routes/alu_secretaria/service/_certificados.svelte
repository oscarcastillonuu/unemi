<script lang="ts">
	import Swal from 'sweetalert2';
	import { addToast } from '$lib/store/toastStore';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { onMount } from 'svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import ComponenteInformacion from './_contenidoInformacion.svelte';
	import { loading } from '$lib/store/loadingStore';
	import Select from 'svelte-select/Select.svelte'; //https://github.com/rob-balfre/svelte-select
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	//import Input from '$components/Forms/Input.svelte'
	import { addNotification } from '$lib/store/notificationStore';
	import { Button, Icon, Spinner, Tooltip,Modal, ModalBody, ModalFooter, ModalHeader  } from 'sveltestrap';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import ComponenteFormSubir from "./_formsubirsolicitud.svelte";

	const dispatch = createEventDispatcher();

	export let eServicio;
	export let eCertificados;
	export let dataExtras;
	export let eMallaCulminada;
	let items_periodos = [];
	let items_matriculas = [];
	let eMatriculas = [];
	let item_matricula,
		ePeriodo,
		eInscripcion,
		ePersona = {};
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	let modalSize = 'sm';
	let id_matricula = 0;
	let id_inscripcion = 0;
	let total_pedidos = 0;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);


	//Variables mimodal
	let aDataModalArchivo = {};
	let modalDetalleContentArchivo;
	let mOpenModalGenericoArchivo = false;
	let modalTitleArchivo = '';
	let modalSizeArchivo = 'sm';
	const mToggleModalGenericoArchivo = () => (mOpenModalGenericoArchivo = !mOpenModalGenericoArchivo);

	onMount(async () => {
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			ePeriodo = dataSession['periodo'];
			eInscripcion = dataSession['inscripcion'];
			ePersona = dataSession['persona'];

			const ePeriodos = dataSession['periodos'];
			//items_periodos.push({ value: '0', label: '--NINGUNO--' });
			for (const i in ePeriodos) {
				items_periodos.push({ value: ePeriodos[i]['id'], label: ePeriodos[i]['nombre_completo'] });
			}
			id_matricula = item_matricula ? item_matricula.value : 0;
			id_inscripcion = eInscripcion['id'];
		}
	});
	$: {
		if (dataExtras) {
			//console.log(dataExtras);
			eMatriculas = dataExtras['eMatriculas'];
			//console.log(eMatriculas);
			for (const i in eMatriculas) {
				if (eMatriculas[i]['nivel']['periodo']['id'] === ePeriodo['id']) {
					item_matricula = {
						value: eMatriculas[i]['id'],
						label: eMatriculas[i]['nivel']['periodo']['nombre']
					};
				}
				items_matriculas.push({
					value: eMatriculas[i]['id'],
					label: eMatriculas[i]['nivel']['periodo']['nombre']
				});
			}
			id_matricula = item_matricula ? item_matricula.value : 0;
		}
		//console.log(id_matricula);
	}

	function handleSelect(event) {
		//console.log(event.detail);
		id_matricula = event.detail.value;
		console.log(id_matricula);
	}
	
	const searchPeriodo =async (id) => {
		
	}

	function handleClear(e) {
		//favouriteFood = undefined;
		//console.log(e);
		id_matricula = 0;
	}

	const openInformacion = (eCertificado) => {
		aDataModal = { eProducto: eCertificado };
		modalDetalleContent = ComponenteInformacion;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = `Información del certificado`;
		modalSize = 'xs';
	};

	const loadAjax = async (data, url) =>
		new Promise(async (resolve, reject) => {
			const [res, errors] = await apiPOST(fetch, url, data);
			//console.log(errorsCertificates);
			if (errors.length > 0) {
				reject({
					error: true,
					message: errors[0].error
				});
			} else {
				resolve({
					error: false,
					value: res
				});
			}
		});
	const parms_type_format_ireport = async (type: undefined) => {
		let parms = '';
		if (type != undefined) {
			parms = 'pdf';
		} else if (type.indexOf('pdf') !== -1) {
			parms = 'pdf';
		} else if (type.indexOf('docx') !== -1) {
			parms = 'docx';
		} else if (type.indexOf('xlsx') !== -1) {
			parms = 'xlsx';
		} else if (type.indexOf('csv') !== -1) {
			parms = 'csv';
		}

		return parms;
	};
	const action_to_download = async (eCertificado: object, valido = '0'): Promise<void> => {
		let parms = {};
		let res = undefined;
		loading.setLoading(true, 'Cargando, espere por favor...');
		if (eCertificado.certification_type === 1) {
			parms['n'] = eCertificado.report.name;
			parms['valido'] = valido
			if (eCertificado.report.version === 2) parms['vqr'] = id_matricula;
			else parms['variableqr'] = id_matricula;

			res = await action_print_ireport(eCertificado.report.types, parms);
		} else if (eCertificado.certification_type === 2) {
			parms['n'] = eCertificado.report.name;
			parms['valido'] = valido
			if (eCertificado.report.version === 2) parms['vqr'] = id_inscripcion;
			else parms['variableqr'] = id_inscripcion;

			res = await action_print_ireport(eCertificado.report.types, parms);
		} else if (eCertificado.certification_type === 3) {
			let id_tipo_periodo = 0;
			let is_cerrada = false;
			for (let i in eMatriculas) {
				if (eMatriculas[i]['id'] === id_matricula) {
					id_tipo_periodo = eMatriculas[i]['nivel']['periodo']['tipo']['orden_id'];
					is_cerrada = eMatriculas[i]['cerrada'];
				}
			}

			if (id_tipo_periodo === 2) {
				if (!is_cerrada) {
					const mensaggeWarning = {
						toast: true,
						position: 'top-center',
						type: 'warning',
						icon: 'warning',
						title: 'Certificado no puede ser generado, periodo académico en curso.',
						showConfirmButton: true,
						timer: 6000
					};
					Swal.fire(mensaggeWarning);
					return;
				}
			}
			parms['n'] = eCertificado.report.name;
			if (eCertificado.report.version === 2) parms['vqr'] = id_matricula;
			else parms['variableqr'] = id_matricula;
			parms['valido'] = valido

			res = await action_print_ireport(eCertificado.report.types, parms);
		}

		if (res !== undefined) {
			if (res.data.es_background) {
				const noti = {
					position: 'top-center',
					type: 'info',
					icon: 'info',
					title: res.message,
					showConfirmButton: true
				};
				Swal.fire(noti);
			} else {
				window.open(`${res.data.reportfile}`, '_blank');
			}
		}
		loading.setLoading(false, 'Cargando, espere por favor...');

		return;
	};

	const sendRequest = async (eCertificado) => {
		let parms = {};
		//loading.setLoading(true, 'Cargando, espere por favor...');
		if (eCertificado.certification_type === 1) {
			parms['n'] = eCertificado.report.name;
			if (eCertificado.report.version === 2) parms['vqr'] = id_matricula;
			else parms['variableqr'] = id_matricula;
		} else if (eCertificado.certification_type === 2) {
			parms['n'] = eCertificado.report.name;
			if (eCertificado.report.version === 2) parms['vqr'] = id_inscripcion;
			else parms['variableqr'] = id_inscripcion;
		} else if (eCertificado.certification_type === 3) {
			let id_tipo_periodo = 0;
			let is_cerrada = false;
			for (let i in eMatriculas) {
				if (eMatriculas[i]['id'] === id_matricula) {
					id_tipo_periodo = eMatriculas[i]['nivel']['periodo']['tipo']['orden_id'];
					is_cerrada = eMatriculas[i]['cerrada'];
				}
			}

			if (id_tipo_periodo === 2) {
				if (!is_cerrada) {
					const mensaggeWarning = {
						toast: true,
						position: 'top-center',
						type: 'warning',
						icon: 'warning',
						title: 'Certificado no puede ser generado, periodo académico en curso.',
						showConfirmButton: true,
						timer: 6000
					};
					Swal.fire(mensaggeWarning);
					return;
				}
			}
			parms['n'] = eCertificado.report.name;
			if (eCertificado.report.version === 2) parms['vqr'] = id_matricula;
			else parms['variableqr'] = id_matricula;
		}
		const format = await parms_type_format_ireport(eCertificado.report.types);
		parms['rt'] = format
		eCertificado['parametros'] = parms;
		
		if (eCertificado.reqmallaculminada == true && eMallaCulminada == '0') {
			const mensaje = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${
					ePersona.nombre_completo
				},no puede descargar el certificado <b>${eCertificado.name}</b> porque no ha culminado la malla de su programa de maestría.</br>
				<p>Una vez culminada su malla podrá solicitar este certificado.</p>`,
				type: 'info',
				icon: 'info',
				showCancelButton: true,
				showConfirmButton: false,
				allowOutsideClick: false,
				cancelButtonColor: '#E99B40',
				cancelButtonText: 'Cerrar'
			};

			Swal.fire(mensaje)
		} else if (eServicio.proceso == 8){
			loadsolicitudfisica(eCertificado);		
		} else {
			const mensaje = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${
					ePersona.nombre_completo
				}, el certificado <b>${eCertificado.name}</b> ${
					eCertificado.cost > 0
						? `tiene un costo <span class="badge bg-warning text-dark">$${eCertificado.cost}</span>`
						: 'no tiene costo'
				} </br><b>¿Está ${ePersona.sexo_id === 1 ? 'segura' : 'seguro'} de ${
					eCertificado.cost > 0 ? 'solicitar' : 'descargar'
				}?</b><br>
				Recuerde que no hay reembolsos, si el producto(certificado) entregado no es el deseado.`,
				type: 'warning',
				icon: 'warning',
				showCancelButton: true,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(25, 135, 84)',
				cancelButtonColor: '#d33',
				confirmButtonText: `Sí, ${ePersona.sexo_id === 1 ? 'segura' : 'seguro'}`,
				cancelButtonText: 'No, cancelar'
			};

			Swal.fire(mensaje)
				.then(async (result) => {
					if (result.value) {
						if (eCertificado.cost > 0) {
							loading.setLoading(true, 'Cargando, espere por favor...');
							loadAjax(
								{
									action: 'addRequest',
									product: 'certificado',
									aData: JSON.stringify(eCertificado)
								},
								'alumno/secretary/solicitud'
							)
								.then((response) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									if (response.value.isSuccess) {
										total_pedidos += 1;
										dispatch('actionRun', { action: 'totalPedidos', value: total_pedidos });
										addToast({ type: 'success', header: 'Exitoso!', body: response.value.message });
										const mensajeOtro = {
											title: `NOTIFICACIÓN`,
											html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${
												ePersona.nombre_completo
											}, desea agregar o descargar otro certificado`,
											type: 'info',
											icon: 'info',
											showCancelButton: true,
											allowOutsideClick: false,
											confirmButtonColor: 'rgb(25, 135, 84)',
											cancelButtonColor: '#0d6efd',
											confirmButtonText: `Sí`,
											cancelButtonText: 'No, ir a mis pedidos'
										};
										Swal.fire(mensajeOtro).then(async (result) => {
											if (result.value) {
												addToast({
													type: 'info',
													header: 'Información',
													body: 'Puede seguir agregando o descargando mas certificados'
												});
											} else {
												goto('/alu_secretaria/mis_pedidos');
											}
										});
									} else {
										loading.setLoading(false, 'Cargando, espere por favor...');
										//addNotification({ msg: response.value.message, type: 'error' });
										addToast({
											type: 'error',
											header: 'Lo sentimos :(',
											body: response.value.message
										});
									}
								})
								.catch((error) => {
									loading.setLoading(false, 'Cargando, espere por favor...');
									//addNotification({ msg: error.message, type: 'error' });
									addToast({ type: 'error', header: 'Lo sentimos :(', body: error.message });
								});
						} else {
							loading.setLoading(true, 'Cargando, espere por favor...');
							await action_to_download(eCertificado);
							loading.setLoading(false, 'Cargando, espere por favor...');
						}
					}
				})

				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					//addNotification({ msg: error.message, type: 'error' });
					addToast({ type: 'error', header: 'Lo sentimos :(', body: error.message });
				});
		}
	};

	const actionRun = (event) => {
		//console.log(event.detail);
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModalSubir') {
			closeModalGenericoArchivo();
		}
	};
	const searchCertificados = (e) => {
		//console.log(e);
		//console.log('externo');
		const cols = document.querySelectorAll(`#rowCertificado_${eServicio.id} .col`);
		//console.log(cols);
		for (let i = 0; i < cols.length; i++) {
			const col = cols[i];
			const nombre = col.querySelector('.certificado_name');
			//console.log('nombre_externo: ', nombre_externo.innerText);
			if (
				converToAscii(nombre.innerText.toLowerCase()).indexOf(converToAscii(e.toLowerCase())) === -1
			) {
				col.style.display = 'none';
			} else {
				col.style.display = '';
			}
		}
	};
	const loadsolicitudfisica = (eCertificado) =>{
		aDataModalArchivo = {eCertificado:eCertificado, idcerti:eCertificado.idsinencryptar};
		modalSizeArchivo = "xl"
		modalDetalleContentArchivo = ComponenteFormSubir;
		mOpenModalGenericoArchivo = !mOpenModalGenericoArchivo;
		modalTitle = 'Añadir solicitud de certificado';
	}
	const closeModalGenericoArchivo = () =>{
		mOpenModalGenericoArchivo = false;
	}
</script>

{#if eCertificados}
	<div class="row mb-4">
		<div class="col-lg-12 col-md-12 col-12 mb-2">
			{#if items_periodos}
				<form>
					<Select
						id="select_periodo"
						items={items_matriculas}
						value={item_matricula}
						on:select={handleSelect}
						on:clear={handleClear}
						isClearable={false}
						placeholder="Seleccione un periodo académico"
					/>
				</form>
			{/if}
		</div>
	</div>
	<div class="row mb-4">
		<div class="col-12">
			<input
				type="search"
				class="form-control"
				placeholder="Buscar certificado"
				style="width: 100% !important;"
				on:keyup={({ target: { value } }) => searchCertificados(value)}
			/>
		</div>
	</div>
	<div
		class="row row-cols-1 row-cols-xxl-5 row-cols-xl-4 row-cols-lg-3 row-cols-md-3 row-cols-sm-2 g-4"
		id="rowCertificado_{eServicio.id}"
	>
		{#each eCertificados as eCertificado}
			<div class="col mb-4">
				<!-- card -->
				<div class="card mb-4 card-hover border border-2 shadow-none h-100 position-relative">
					<!-- img -->
					{#if eCertificado.cost > 0}
						<span
							class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark"
							style="background-color: #fc7e00 !important;"
						>
							${eCertificado.cost}
							<!--<span class="visually-hidden">unread messages</span>-->
						</span>
					{/if}
					<div class="card-img-top">
						<img src={eCertificado.imagen} alt="" class="rounded-top-md img-fluid" />
					</div>
					<!-- card body -->
					<div class="card-body mb-0 pb-0">
						<h5 class="card-title h3 text-center certificado_name">{eCertificado.name}</h5>
						{#if eCertificado.validity}
							<p class="card-text text-muted text-center">
								Tiempo de validez:
								<!--{eCertificado.validity_display}-->
								{#if eCertificado.validity.type === 0}
									<span class="badge bg-badge">No aplica</span>
								{:else if eCertificado.validity.type == 1}
									<span class="badge bg-danger">{eCertificado.validity.display}</span>
								{:else if eCertificado.validity.type == 2}
									<span class="badge bg-warning text-dark">{eCertificado.validity.display}</span>
								{:else if eCertificado.validity.type == 3}
									<span class="badge bg-success">{eCertificado.validity.display}</span>
								{:else if eCertificado.validity.time > 1}
									<span class="badge bg-info text-dark">{eCertificado.validity.display}</span>
								{:else}
									<span class="badge bg-info text-dark">{eCertificado.validity.display}</span>
								{/if}
							</p>
						{/if}
						<!--<h3 class="mb-3 fw-semi-bold text-center">
							{eProducto.name}
						</h3>
						<p class="mb-3">{eProducto.description}</p>-->
					</div>
					<div class="card-footer text-muted">
						<div>

							<!-- {#if eServicio.costo > 0}
								
							{/if} -->
							<div class="lh-1 d-flex justify-content-between">
								<div>
									{#if eCertificado.idsinencryptar === 58 || eCertificado.idsinencryptar === 59}
									<button
										type="button"
										class="btn btn-primary btn-sm"
										on:click|preventDefault={() => sendRequest(eCertificado)}
										><Icon name='cart-plus'/>
										Solicitar</button
									>	
									{:else}
									<button
										type="button"
										class="btn {eCertificado.cost > 0 ? 'btn-primary' : 'btn-info text-black'} btn-sm"
										on:click|preventDefault={() => sendRequest(eCertificado)}
										><Icon name={eCertificado.cost > 0 ? 'cart-plus' : 'download'} />
										{eCertificado.cost > 0 ? 'Solicitar' : 'Descargar'}</button
									>	
									{/if}
								</div>	
								<div>
									<button
										type="button"
										class="btn btn-sm btn-secondary"
										on:click|preventDefault={() => openInformacion(eCertificado)}
										><Icon name="info-lg" /> Información</button
									>
								</div>
							</div>	

							<!-- <div>
								<button
									type="button"
									class="btn {eServicio.costo > 0 ? 'btn-primary' : 'btn-info text-black'} btn-sm"
									on:click|preventDefault={() => sendRequest(eCertificado)}
									><Icon name={eServicio.costo > 0 ? 'cart-plus' : 'download'} />
									{eServicio.costo > 0 ? 'Solicitar' : 'Descargar'}</button
								>
							</div> -->

							{#if eCertificado.proceso !== 8}
								<div class="mt-2" style="display: flex; justify-content: center">
									<button
										type="button"
										class="btn btn-sm btn-warning"
										on:click|preventDefault={() => action_to_download(eCertificado, '1')}
										><i class="bi bi-eye-fill"></i> Pre-visualizar certificado</button>
								</div>
							{/if}							
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>
{:else}
	<div class="row">
		<div class="col-12">No existe certificados</div>
	</div>
{/if}

{#if mOpenModalGenericoArchivo}
<Modal 
	isOpen={mOpenModalGenericoArchivo}
	toggle={mToggleModalGenericoArchivo}
	size={modalSizeArchivo}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}>

<ModalHeader>
	<h4>Subir evidencia</h4>
</ModalHeader>
	<ModalBody>
		<svelte:component this={modalDetalleContentArchivo} {aDataModalArchivo} on:actionRun={actionRun} />
	</ModalBody>
</Modal>
{/if}

{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={aDataModal}
		size={modalSize}
		on:actionRun={actionRun}
	/>
{/if}
