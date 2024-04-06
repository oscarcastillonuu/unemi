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
	export let eTitulaciones;
	export let eSolicitudHom;
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

	const openInformacion = (eTitulacion) => {
		aDataModal = { eProducto: eTitulacion };
		modalDetalleContent = ComponenteInformacion;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = `Información del producto`;
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

    const sendRequest = async (eTitulacion) => {
        const mensaje = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${
					ePersona.nombre_completo
				},  la elaboración del informe académico de pertinencia, con el propósito de evaluar su aplicabilidad al proceso de <b>${eTitulacion.name} </b>, ${
					eTitulacion.cost > 0
						? `tiene un costo de <span class="badge bg-warning text-dark">$${eTitulacion.cost}</span>`
						: 'no tiene costo'
				} </br><b>¿Está ${ePersona.sexo_id === 1 ? 'segura' : 'seguro'} de solicitar? </b><br>
				Recuerde que no hay reembolsos, si el resultado no es favorable. En caso de recibir una respuesta favorable tendrá que cancelar un valor de <span class="badge bg-warning text-dark">$${eTitulacion.cost2modules}</span>, equivalente a los dos módulos de titulación del programa de maestría.`,
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
						if (eTitulacion.cost > 0) {
							loading.setLoading(true, 'Cargando, espere por favor...');
							loadAjax(
								{
									action: 'addRequest',
									product: 'titulacion',
									aData: JSON.stringify(eTitulacion)
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
											}, su solicitud ha sido emitida correctamente`,
											type: 'info',
											icon: 'info',
											showCancelButton: true,
											showConfirmButton:false,
											allowOutsideClick: false,
											cancelButtonColor: '#0d6efd',
											cancelButtonText: 'Ir a mis pedidos'
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
						}
					}
				})

				.catch((error) => {
					loading.setLoading(false, 'Cargando, espere por favor...');
					//addNotification({ msg: error.message, type: 'error' });
					addToast({ type: 'error', header: 'Lo sentimos :(', body: error.message });
				});
    };
    
	const alerta_homologa = async (eTitulacion) => {
		var message = ''
		if (eTitulacion.homologa === '1') {
			message = `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${ePersona.nombre_completo},no puede realizar la 
					solicitud de <b>${eTitulacion.name}</b> porque ya se encuentra graduado en el programa de <b>${eTitulacion.carrera}</b>.`
		} else if (eTitulacion.homologa === '2') {
			message = `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${ePersona.nombre_completo},no puede realizar la 
					solicitud de <b>${eTitulacion.name}</b> porque la cohorte del programa de <b>${eTitulacion.carrera}</b> ya ha iniciado 
					su primer módulo.`
		} else if (eTitulacion.homologa === '3') {
			message = `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${ePersona.nombre_completo},no puede realizar la 
					solicitud de <b>${eTitulacion.name}</b> porque no ha realizado el pago de la primera cuota o de la 
					totalidad del programa de <b>${eTitulacion.carrera}</b> para ser considerado como inscrito.`
		}
										
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: message,
			type: 'info',
			icon: 'info',
			showCancelButton: true,
			showConfirmButton: false,
			allowOutsideClick: false,
			cancelButtonColor: '#E99B40',
			cancelButtonText: 'Cerrar'
		};

		Swal.fire(mensaje)
	}

	const actionRun = (event) => {
		//console.log(event.detail);
		const detail = event.detail;
		const action = detail.action;
		if (action == 'closeModalSubir') {
			closeModalGenericoArchivo();
		}
	};

/*	const searchCertificados = (e) => {
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
	};*/

	const closeModalGenericoArchivo = () =>{
		mOpenModalGenericoArchivo = false;
	}
</script>

{#if eTitulaciones}
<!--	<div class="row mb-4">
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
	</div>--->

	<div class="row row-cols-1 row-cols-xxl-5 row-cols-xl-4 row-cols-lg-3 row-cols-md-3 row-cols-sm-2 g-4" 
		id="rowCertificado_{eServicio.id}">

		{#each eTitulaciones as eTitulacion}
			<div class="col mb-4">
				<!-- card -->
				<div class="card mb-4 card-hover border border-2 shadow-none h-100 position-relative">
					<!-- img -->
					{#if eTitulacion.cost > 0}
						<span
							class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning text-dark"
							style="background-color: #fc7e00 !important;"
						>
							${eTitulacion.cost}
							<!--<span class="visually-hidden">unread messages</span>-->
						</span>
					{/if}
					<div class="card-img-top">
						<img src={eTitulacion.imagen} alt="" class="rounded-top-md img-fluid" />
					</div>
					<!-- card body -->
					<div class="card-body mb-0 pb-0">
						<h5 class="card-title h3 text-center certificado_name">{eTitulacion.name}</h5>
							<p class="card-text text-muted text-center">
								Tiempo de respuesta una vez procesado el pago: <span class="badge bg-success">72 horas</span>
						<!--		{eTitulacion.validity_display}
								{#if eTitulacion.validity.type === 0}
									<span class="badge bg-badge">No aplica</span>
								{:else if eTitulacion.validity.type == 1}
									<span class="badge bg-danger">{eTitulacion.validity.display}</span>
								{:else if eTitulacion.validity.type == 2}
									<span class="badge bg-warning text-dark">{eTitulacion.validity.display}</span>
								{:else if eTitulacion.validity.type == 3}
									<span class="badge bg-success">{eTitulacion.validity.display}</span>
								{:else if eTitulacion.validity.time > 1}
									<span class="badge bg-info text-dark">{eTitulacion.validity.display}</span>
								{:else}
									<span class="badge bg-info text-dark">{eTitulacion.validity.display}</span>
								{/if}-->
							</p>
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
									{#if eTitulacion.idsin === 1}
										<button
											type="button"
											class="btn {eTitulacion.cost > 0 ? 'btn-primary' : 'btn-info text-black'} btn-sm"
											on:click|preventDefault={() => sendRequest(eTitulacion)}
											><Icon name={eTitulacion.cost > 0 ? 'cart-plus' : 'download'} />
											{eTitulacion.cost > 0 ? 'Solicitar' : 'Descargar'}</button>
									{:else}
										{#if eSolicitudHom}
												<a type="button" 
												href=""
												on:click|preventDefault={() => goto('/alu_secretaria/service/asignaturashomologa')}
												class="btn btn-warning btn-sm"
												><Icon name='cart-plus'/> Ver solicitud</a>
										{:else}
											{#if eTitulacion.homologa === '0'}			
												<a type="button" 
												href=""
												on:click|preventDefault={() => goto('/alu_secretaria/service/asignaturashomologa')}
												class="btn btn-primary btn-sm"
												><Icon name='cart-plus'/> Solicitar</a>
											{:else}
												<button
													type="button"
													class="btn {eTitulacion.cost > 0 ? 'btn-primary' : 'btn-info text-black'} btn-sm"
													on:click|preventDefault={() => alerta_homologa(eTitulacion)}
													><Icon name={eTitulacion.cost > 0 ? 'cart-plus' : 'download'} />
													{eTitulacion.cost > 0 ? 'Solicitar' : 'Descargar'}</button>
											{/if}
										{/if}		
									{/if}
								</div>	
								<div>
									<button
										type="button"
										class="btn btn-sm btn-secondary"
										on:click|preventDefault={() => openInformacion(eTitulacion)}
										><Icon name="info-lg" /> Información</button
									>
								</div>
							</div>								
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>
{:else}
	<div class="row">
		<div class="col-12">No existen productos para esta categoría</div>
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
