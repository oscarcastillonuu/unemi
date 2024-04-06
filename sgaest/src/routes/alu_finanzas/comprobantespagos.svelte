<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	import { variables } from '$lib/utils/constants';

	let eComprobantesLista = {};
	let ePersona = [];
	let eMatricula = [];
	let eRubros = {};
	export const load: Load = async ({ fetch }) => {
		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
				action: 'comprobantespagos'
			});
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/alu_finanzas'
				};
			} else {
				if (!res.isSuccess) {
					if (!res.module_access) {
						if (res.redirect) {
							if (res.token) {
								return (window.location.href = `${connectionToken}&ret=/${res.redirect}`);
							} else {
								addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
								return {
									status: 302,
									redirect: `/${res.redirect}`
								};
							}
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return {
								status: 302,
								redirect: '/'
							};
						}
					} else {
						addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
					}
				} else {
					//console.log(res.data);
					eComprobantesLista = res.data['eComprobantesLista'];
					eMatricula = res.data['eMatricula'];
					ePersona = res.data['ePersona'];
				}
			}
		}
		return {
			props: {
				eComprobantesLista,
				eMatricula,
				ePersona
			}
		};
	};
</script>

<script lang="ts">
	import { addToast } from '$lib/store/toastStore';
	import { browserGet, apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Spinner, Tooltip } from 'sveltestrap';
	import Swal from 'sweetalert2';
	import { goto } from '$app/navigation';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';
	import { dataset_dev, each } from 'svelte/internal';
	import HistorialComprobantePago from './_historialcomprobante.svelte';
	import MultiSelect from './_multiselect.svelte';
	const dispatch = createEventDispatcher();
	let load = true;
	let open = false;
	let itemsBreadCrumb = [
		{ text: 'Mis Finanzas', active: false, href: '/alu_finanzas' },
		{ text: 'Comprobantes', active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/alu_finanzas', text: 'Atrás' };

	//Formulario registro de pago
	let mSizeComprobante = 'lg';
	let mOpenComprobante = false;
	const mToggleComprobante = () => (mOpenComprobante = !mOpenComprobante);
	let titleComprobante;

	//Modal historial
	let mOpenHistorialComp = false;

	//Registro de comprobantes
	let celularcomprobante = '';
	let emailpersonalcomprobante = '';
	let valorComprobante = 0;
	let pondComprobantePagoF;
	let cuentaBanco;
	let cuentaBanco_id = '';
	let tipoComprobante;
	let tipoComprobante_id = '';
	let fechaPagoComprobante = formatDate(new Date());
	let observacionComprobante = '';
	let referenciapapeletaComprobante = '';
	let nameComrpobantePagoF = 'fileComrpobantePagoF';
	let previusValue = 0.00;
	let id_comprobantepago = 0;
	let comprobantePagoArchivo = '';
	let availableValues = [];
	let selectedValues = [];
	let showLabelTipo = false;
	let sumaValores = 0.00;

	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
	let eHistorialComp = {};
	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {
		registerPlugin(FilePondPluginFileValidateType);
		if (ePersona) {
			load = false;
		}
	});

	//Registro comprobante de pago
	const handleAddFileComprobantePago = (err, fileItem) => {
		console.log(pondComprobantePagoF.getFiles());
		console.log('A file has been added', fileItem);
	};
	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	function soloNumeros(node, value) {
		return {
			update(value) {
				valorComprobante =
					value === null || valorComprobante < node.min ? previusValue : parseFloat(value);
				previusValue = 0.00;
			}
		};
	}

	function padTo2Digits(num) {
		return num.toString().padStart(2, '0');
	}

	function formatDate(date) {
		return [
			date.getFullYear(),
			padTo2Digits(date.getMonth() + 1),
			padTo2Digits(date.getDate())
		].join('-');
	}
	const openComprobante = async () => {
		limpiarcampos();
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'cuentasbancarias'
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				cuentaBanco = res.data['eCuentasBancaria'];
				celularcomprobante = res.data['eCelular'];
				emailpersonalcomprobante = res.data['eCorreo'];
				tipoComprobante = res.data['eTipoComrpobante'];
				fechaPagoComprobante = formatDate(new Date());
				eRubros = res.data['eRubros'];
				//console.log(eRubros);
				availableValues = [];
				selectedValues = [];
				if (eRubros.length >0){
					for(let rub of eRubros)
					{ 
						availableValues.push( {'id':rub.id,'name':rub.display,'valor':rub.saldo})
					}
				}
				//console.log(availableValues);
			}
		}
		mSizeComprobante = 'lg';
		mOpenComprobante = true;
		titleComprobante = 'Registro de comprobantes';
	};

	const openHistorialComp = async (id) => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'historialcomprobantes',
			id: id
		});
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {				
				eHistorialComp = res.data;
				modalDetalleContent = HistorialComprobantePago;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Historial de Aprobación';
			}
		}
	};

	const openComprobanteEditar = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
			action: 'cuentasbancarias',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				cuentaBanco = res.data['eCuentasBancaria'];
				celularcomprobante = res.data['eCelular'];
				emailpersonalcomprobante = res.data['eCorreo'];
				tipoComprobante = res.data['eTipoComrpobante'];
				let fecha = res.data['eComprobante'].fechapago.split('-');
				fechaPagoComprobante = formatDate(
					new Date(parseInt(fecha[0]), parseInt(fecha[1]) - 1, parseInt(fecha[2]))
				);
				//console.log(res.data['eComprobante']);
				valorComprobante = res.data['eComprobante'].valor;
				comprobantePagoArchivo = res.data['eComprobante'].comprobantes;
				//cuentaBanco_id = res.data['eComprobante'].cuentabancaria.id;
				tipoComprobante_id = res.data['eComprobante'].tipocomprobante;
				console.log(tipoComprobante_id)
				observacionComprobante = res.data['eComprobante'].observacion;
				referenciapapeletaComprobante = res.data['eComprobante'].referenciapapeleta;
				let rubrosedi = res.data['eRubrosId'];
				nameComrpobantePagoF = 'fileComrpobantePagoF';
				id_comprobantepago = res.data['eComprobante'].id;
				previusValue = 0.00;
				eRubros = res.data['eRubros'];
				if (tipoComprobante_id == 1){
					showLabelTipo = true;
				}else{
					showLabelTipo = false;
				}
				//console.log(eRubros)
				availableValues = [];
				selectedValues = [];
				if (eRubros.length >0){
					for(let rub of eRubros)
					{ 
						availableValues.push( {'id':rub.id,'name':rub.display,'valor':rub.saldo})
					}
				}
				if (rubrosedi.length > 0){
					for(let rub of rubrosedi){
						selectedValues.push(rub)
					}
				}
			}
		}
		mSizeComprobante = 'lg';
		mOpenComprobante = true;
		titleComprobante = 'Registro de comprobantes';
	};

	const limpiarcampos = () => {
		valorComprobante = 0;
		pondComprobantePagoF;
		cuentaBanco_id = '';
		tipoComprobante_id = '';
		fechaPagoComprobante = formatDate(new Date());
		observacionComprobante = '';
		previusValue = 0.00;
		comprobantePagoArchivo = '';
		referenciapapeletaComprobante = '';
		showLabelTipo = false;
	};

	const closeComprobanteForm = () => {
		mOpenComprobante = false;
	};
	const closeHistorialComp = () => {
		mOpenHistorialComp = false;
	};
	const loadAjax = async (data, url, method = undefined) => {
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
				const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
				action: 'comprobantespagos'
			});
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
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
				if (errors.length > 0) {
					console.log(errors);
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
			}
		});
	};

	const loadInitial = () => {
		new Promise((resolve, reject) => {
			const ds = browserGet('dataSession');
			const dataSession = JSON.parse(ds);
			const matricula = dataSession['matricula'];
			loadAjax({}, 'alumno/finanza')
				.then((response) => {
					if (response.value.isSuccess) {
						eComprobantesLista = response.value.data['eComprobantesLista'];
						ePersona = response.value.data['ePersona'];
						eMatricula = response.value.data['eMatricula'];

						resolve({
							error: false,
							value: true
						});
					} else {
						reject({
							error: true,
							message: response.value.message
						});
					}
				})
				.catch((error) => {
					reject({
						error: true,
						message: error.message
					});
				});
		});
	};

	const saveComprobantePago = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmComprobantePago = document.querySelector('#frmComprobantePago');
		const formData = new FormData($frmComprobantePago);
		const numeros = /^([0-9])*$/;
		let rubroscom = document.getElementsByClassName("token");
		let rubros_id = [];
		for(let id of rubroscom){
			rubros_id.push(id.attributes['data-id'].value)
		}
		formData.append('action', 'addcomprobantepago');
		console.log(eMatricula.id)
		formData.append('id_matri', eMatricula.id);
		formData.append('id_comprobante', id);
		formData.append('rubros_id[]',JSON.stringify(rubros_id))

		let celular = document.getElementById('eCelularCom');
		//let cuentabancaria = document.getElementById('eCuentaBancoComrp');
		let observacion = document.getElementById('eObservacionComprobante');
		let tipocomprobantebanco = document.getElementById('eTipoCuentaBancoComrp');
		let valordigitado = document.getElementById('eValorComprobante');

		/*if (
			cuentabancaria.value === null ||
			cuentabancaria.value === undefined ||
			cuentabancaria.value === ''
		) {
			addNotification({
				msg: 'Seleccione la cuenta bancaria',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}*/
		if (rubros_id.length <1){
			addNotification({
				msg: 'Seleccione al menos un rubro',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (!celular.value.match(numeros)) {
			addNotification({
				msg: 'Celular debe ser numeros',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (observacion.value === null || observacion.value === undefined || observacion.value === '') {
			addNotification({
				msg: 'Llene el campo observación',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		if (
			tipocomprobantebanco.value === null ||
			tipocomprobantebanco.value === undefined ||
			tipocomprobantebanco.value === ''
		) {
			addNotification({
				msg: 'Seleccione el tipo de comprobante',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		}
		
		if (parseInt(tipocomprobantebanco.value) === 1){
			let referenciapapeleta = document.getElementById('eReferenciaPapeletaId');
			if (referenciapapeleta.value === null || referenciapapeleta.value === undefined || referenciapapeleta.value === '') {
				addNotification({
					msg: 'Llene el campo No. Papeleta',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
		}
		if (!id) {
			let fileDocumento = pondComprobantePagoF.getFiles();
			if (fileDocumento.length == 0) {
				addNotification({
					msg: 'Debe subir un archivo',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
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
			if (pondComprobantePagoF && pondComprobantePagoF.getFiles().length > 0) {
				eFileDocumento = pondComprobantePagoF.getFiles()[0];
			}
			formData.append('eFileComrpobantePagoF', eFileDocumento.file);
		}else{
			let fileDocumento = pondComprobantePagoF.getFiles();
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
			if (pondComprobantePagoF && pondComprobantePagoF.getFiles().length > 0) {
				eFileDocumento = pondComprobantePagoF.getFiles()[0];
			}
			if (eFileDocumento){
				formData.append('eFileComrpobantePagoF', eFileDocumento.file);
			}
		}
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/finanzas', formData);
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
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				//dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenComprobante = false;
				limpiarcampos();
				Swal.fire('Registro guardado con exito!','La recaudación de los pagos registrados se realizará las próximas 72hrs','info')
				.then(() => {
					location.reload();
					/*loadAjax(
						{
							action: 'comprobantespagos'
						},
						'alumno/finanzas'
					).then((response) => {
						console.log(response);
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {

								loadInitial()

								addNotification({
								msg: 'Registro guardado con éxito.!',
								type: 'info'
								});
							} else {
								addNotification({
									msg: response.value.message,
									type: 'error'
								});
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({
								msg: error.message,
								type: 'error'
							});
						});*/
				});
				
			}
		}
	};

	const eliminarComprobante = async (id) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted eliminara el comprobante de pago. ¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de eliminar carné estudiantil?`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonText: 'Si, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Eliminando, espere por favor...');
					const [res, errors] = await apiPOST(fetch, 'alumno/finanzas', {
						action: 'deleteComprobantePago',
						id: id
					});
					loading.setLoading(false, 'Eliminando, espere por favor...');
					if (errors.length > 0) {
						addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
						goto('/');
					} else {
						if (!res.isSuccess) {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
						} else {
							addToast({
								type: 'success',
								header: 'Exitoso',
								body: 'Se elimino correctamente el comprobante de pago'
							});
							location.reload();
						}
					}
				} else {
					addToast({
						type: 'info',
						header: 'Enhorabuena',
						body: 'Has cancelado la acción de eliminar comprobante de pago'
					});
				}
			})
			.catch((error) => {
				addToast({ type: 'error', header: 'Ocurrio un error', body: error });
			});
	};
	const handeChangeTComprobante = async (id) => {
		if (id == 1) {
			showLabelTipo = true;
		}else {
			showLabelTipo = false;
		}
	}
	const handleChangeRubros = async () => {
		let vrubrosid = await document.getElementsByClassName('token');
		let valordigitado = await document.getElementById("eValorComprobante");
		let valores_id = 0.00;
		for(let item of vrubrosid){
			valores_id += parseFloat(item.attributes['data-valor'].value)
		}
		valores_id
		if (valores_id != valordigitado)
		{
			addNotification({
					msg: 'El valor total de los rubros no coincide con el valor ingresado',
					type: 'info',
					target: 'newNotificationToast'
				});
		}
	}
</script>

<svelte:head>
	<title>Mis Finanzas - Comprobantes</title>
</svelte:head>
{#if !load}
	<BreadCrumb title="Lista de comprobantes" items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="row">
		<div class="col-12">
			<div class="card mb-4">
				<div class="card-header">
					<a on:click={() => openComprobante()} class="btn btn-info btn-sm"
						><i class="bi bi-file-earmark-plus-fill" /> Agregar Pago</a
					>
				</div>
				<div class="card-body">
					<div class="table-responsive">
						<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
							<thead class="table-light">
								<tr>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>OBSERVACIÓN</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>FECHAS</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>DETALLES</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>ESTADO</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>COMPROBANTE</th
									>
									<th scope="col" class="border-top-0 text-center" style="text-align: center;"
										>ACCIONES</th
									>
								</tr>
							</thead>
							<tbody>
								{#if eComprobantesLista.length > 0}
									{#each eComprobantesLista as compro}
										<tr>
											<td class="fs-6" style="text-align: justify;word-wrap: break-word;">
												{compro.observacion}
											</td>
											<td class="fs-6" style="text-align: left;">
												Fecha de Pago: {compro.fechapago}<br>
												Fecha de Creación: {compro.fecha_creacion}
											</td>
											<td class="fs-6" style="text-align: left;">
												Valor Pagado: <b>${compro.valor}</b><br>
												Valor Rubro: <b>${compro.valorrubros}</b><br>
												{#if compro.referenciapapeleta }Referencia papeleta: <b>{compro.referenciapapeleta}</b><br>{/if}
												<!--<label class="badge badge-pill bg-primary">{compro.cuentabancaria.display}</label><br>-->
												{#if compro.tipocomprobante == 1}											
												<label class="badge badge-pill bg-success">{compro.tipocomprobante_nombre}</label>
												{:else if compro.tipocomprobante == 2}
												<label class="badge badge-pill bg-info">{compro.tipocomprobante_nombre}</label>
												{/if}
											</td>

											<td class="fs-6" style="text-align: center; color: green;">
												{#if compro.estados == 1}
													<span class="badge bg-secondary ">{compro.estados_display}</span>
												{:else if compro.estados == 2}
													<span class="badge bg-info ">{compro.estados_display}</span>
												{:else if compro.estados == 3}
													<span class="badge bg-danger ">{compro.estados_display}</span>
												{:else if compro.estados == 4}
													<span class="badge bg-success ">{compro.estados_display} </span>
												{/if}
											</td>
											<td class="fs-6" style="text-align: center;">
												{#if compro.typefile != '.pdf'}
													<a
														title="VER COMPROBANTE"
														href="{variables.BASE_API}{compro.comprobantes}"
														target="_blank"
														class="btn btn-info btn-sm"><i class="bi bi-file-earmark-image" /></a
													>
												{:else}
													<a
														title="VER COMPROBANTE"
														href="{variables.BASE_API}{compro.comprobantes}"
														target="_blank"
														class="btn btn-info btn-sm"><i class="bi bi-file-earmark-zip" /></a
													>
												{/if}
											</td>
											<td class="fs-6" style="text-align: center;">
												{#if compro.estados != 1}
													<a
														title="HISTORIAL"
														class="btn btn-primary btn-sm"
														on:click={() => openHistorialComp(compro.id)}
														><i class="bi bi-list-task" /></a
													>
												{:else}
													<a
														title="HISTORIAL"
														class="btn btn-primary btn-sm"
														on:click={() => openHistorialComp(compro.id)}
														><i class="bi bi-list-task" /></a
													>
													<a
														title="EDITAR"
														class="btn btn-warning btn-sm"
														on:click={() => openComprobanteEditar(compro.id)}
														><i class="bi bi-pencil-square" /></a
													>
													<a
														title="ELIMINAR"
														class="btn btn-danger btn-sm"
														on:click={() => eliminarComprobante(compro.id)}
														><i class="bi bi-trash"></i>
													</a>
												{/if}
											</td>
										</tr>
									{/each}
								{:else}
									<tr>
										<td colspan="8" class="text-center">NO EXISTEN COMPROBANTES DISPONIBLES</td>
									</tr>
								{/if}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
{:else}
	<div
		class="mt-4 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}

<Modal
	isOpen={mOpenComprobante}
	toggle={mToggleComprobante}
	size={mSizeComprobante}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleComprobante}>
		<h4>{titleComprobante}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmComprobantePago"
			on:submit|preventDefault={() => saveComprobantePago(id_comprobantepago)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">
					<!--<div class="col-md-12">
						<label for="eCuentaBancoComrp" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Cuentas Bancaria:
						</label>
						<select
							class="form-control form-select"
							id="eCuentaBancoComrp"
							name="eCuentaBancoComrp"
							bind:value={cuentaBanco[0].id}
						>
							{#each cuentaBanco as bcuen}
								<option value={bcuen.id} selected>
									{bcuen.display}
								</option>
							{/each}
						</select>
					</div>-->
					<div class="col-md-12">
						<label for="eRubroComp" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Rubro:
						</label>
						<MultiSelect id='lang' value={selectedValues}>
							{#each availableValues as bcuen}
										<option value={bcuen.id} id_valor={bcuen.valor}>
											{bcuen.name}
										</option>
							{/each}
									</MultiSelect>
					</div>
					<div class="col-md-6">
						<label for="eCelularCom" class="form-label fw-bold"> Celular: </label>
						<input
							type="text"
							maxlength="10"
							minlength="10"
							class="form-control"
							id="eCelularCom"
							name="eCelularCom"
							bind:value={celularcomprobante}
						/>
					</div>
					<div class="col-md-6">
						<label for="eCorreoPersonal" class="form-label fw-bold"> Correo personal: </label>
						<input
							type="text"
							class="form-control"
							id="eCorreoPersonal"
							name="eCorreoPersonal"
							bind:value={emailpersonalcomprobante}
						/>
					</div>

					<div class="col-md-6">
						<label for="eFechaPago" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Fecha pago:
						</label>
						<input
							type="date"
							class="form-control"
							id="eFechaPago"
							name="eFechaPago"
							bind:value={fechaPagoComprobante}
						/>
					</div>
					<div class="col-md-6">
						<label for="eValorComprobante" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Valor:
						</label>
						<input
							type="number"
							class="form-control"
							id="eValorComprobante"
							name="eValorComprobante"
							step="0.01"
							min="1"
							bind:value={valorComprobante}
							use:soloNumeros={valorComprobante}
						/>
					</div>
					<div class="col-md-12">
						<label for="eObservacionComprobante" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Observación:
						</label>
						<textarea
							type="text"
							class="form-control"
							id="eObservacionComprobante"
							name="eObservacionComprobante"
							rows="2"
							bind:value={observacionComprobante}
						/>
					</div>
					<div class="col-md-12">
						<label for="eTipoCuentaBancoComrp" class="form-label fw-bold col-md-12"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Tipo de comprobante:
						</label>
						{#if showLabelTipo}
						<div class="row">
							<div class="col-md-6">Comprobante recibido en el banco cuando se llena una papeleta de depósito.
							</div>
							<div class="col-md-6 ms-auto">Comprobante recibido en el banco cuando se presenta cédula de identidad. No es necesario subir este tipo de comprobante.</div>
						</div>
						<img class="col-md-12" src='{variables.BASE_API}/static/images/icons/deposito_recaudo.png'>
						{/if}
						<select
							class="form-control form-select col-md-12"
							id="eTipoCuentaBancoComrp"
							name="eTipoCuentaBancoComrp"
							bind:value={tipoComprobante_id}
							on:change={() => handeChangeTComprobante(tipoComprobante_id)}
						>
							<option value="" selected> ----------------- </option>
							{#each tipoComprobante as bcuen}
								<option value={bcuen[0]}>
									{bcuen[1]}
								</option>
							{/each}
						</select>
						
						{#if showLabelTipo}
						<label for="eReferenciaPapeleta" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> No. Papeleta:
						</label>
						<input
							type="text"
							class="form-control"
							id="eReferenciaPapeletaId"
							name="eReferenciaPapeleta"
							bind:value={referenciapapeletaComprobante}
						/>
						{/if}
					</div>
					<div class="col-md-12">
						<label for="eFileomprobanteForm" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Comprobante de pago:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eFileomprobanteForm"
							bind:this={pondComprobantePagoF}
							{nameComrpobantePagoF}
							name="fileDocumento"
							labelIdle={['<span class="filepond--label-action">Subir archivo</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileComprobantePago}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxFileSize="10MB"
							maxParallelUploads="1"
						/>
						{#if comprobantePagoArchivo != ''}
							<a
								title="VER COMPROBANTE"
								href="{variables.BASE_API}{comprobantePagoArchivo}"
								target="_blank">{comprobantePagoArchivo}</a
							><br />
						{/if}
						<small class="text-warning"
							>Tamaño máximo permitido 10Mb, en formato pdf,png,jpg,jpeg</small
						>
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeComprobanteForm()}
							>Cerrar</a
						>
					</div>
				</div>
			</div>
		</form>
	</ModalBody>
</Modal>
{#if mOpenModalGenerico}
	<ModalGenerico
		mToggle={mToggleModalGenerico}
		mOpen={mOpenModalGenerico}
		modalContent={modalDetalleContent}
		title={modalTitle}
		aData={eHistorialComp}
		size="xl"
	/>
{/if}

<style global>
	@import 'filepond/dist/filepond.css';
</style>
