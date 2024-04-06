<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { browserGet, apiPOST, apiGET, apiPOSTFormData } from '$lib/utils/requestUtils';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';

	let eAsignaturas = [];
	let eSolicitudes = [];
	let solicitud_actual = [];
	let eCarreraPos = [];
	let itemsBreadCrumb = [
		{ text: 'Servicios de secretaria', active: true, href: '/alu_secretaria' },
		{ text: 'Asignaturas a homologar', active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/alu_secretaria', text: 'Atrás' };

	export const load: Load = async ({ fetch }) => {
		const ds = browserGet('dataSession');
		let ePersona = {};
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			ePersona = dataSession['persona'];
			const [res, errors] = await apiGET(fetch, 'alumno/secretary/product', {
				action: 'listaasignaturas'
			});

			//console.log(res);
			if (errors.length > 0) {
				addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
				return {
					status: 302,
					redirect: '/'
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
					console.log(res.data);
					eAsignaturas = res.data['eAsignaturas'];
					eSolicitudes = res.data['eSolicitudes'];
					solicitud_actual = res.data['eSolicitudAct'];
					eCarreraPos = res.data['eCarreraPos'];
				}
			}
		}

		return {
			props: {
				eAsignaturas,
				eSolicitudes,
				solicitud_actual,
				ePersona,
				eCarreraPos
			}
		};
	};
</script>

<script lang="ts">
	import { onMount } from 'svelte';
	import { loading } from '$lib/store/loadingStore';
	import Swal from 'sweetalert2';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import { addNotification } from '$lib/store/notificationStore';
	import { goto } from '$app/navigation';
	import ComponenteRubros from './_rubrosgenerados.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import Grid from 'gridjs-svelte';
	import { h, html } from 'gridjs';

	let grid;
	let valor = false;

	//Formulario firma solicitud
	let mSizeFirmaSolicitud = 'lg';
	let mOpenFirmaSolicitud = false;
	const mToggleFirmaSolicitud = () => (mOpenFirmaSolicitud = !mOpenFirmaSolicitud);
	let titleFirmaSolicitud;
	let pondFirmaSolicitud;
	let nameFirmaSolicitud = 'fileFirmaSolicitud';
	let ePassword = '';

	let titleFirmaSolicitudSign;
	let pondFirmaSolicitudSign;
	let nameFirmaSolicitudSign = 'fileFirmaSolicitudSign';

	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	let modalSize = 'xl';

	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

	export let ePersona;

	onMount(async () => {
		for (let i = 0; i < eAsignaturas.length; i++) {
			let asig = eAsignaturas[i];
			if (asig.homologada == '1') {
				let inputElement = document.getElementById(`checkbox_${asig.pk}`);
				inputElement.checked = true;
				//				console.log(asig.pk, asig.nombre, inputElement);
				//				console.log(solicitud_actual)
			}
		}
	});

	const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFileFirmaSolicitud = (err, fileItem) => {
		console.log(pondFirmaSolicitud.getFiles());
		console.log('A file has been added', fileItem);
	};

	const handleAddFileFirmaSolicitudSign = (err, fileItem) => {
		console.log(pondFirmaSolicitudSign.getFiles());
		console.log('A file has been added', fileItem);
	};

	const closeFirmaSolicitudForm = () => {
		mOpenFirmaSolicitud = false;
	};

	const changetypeval = async (event) => {
		valor = event.target.checked;

		for (let i = 0; i < eAsignaturas.length; i++) {
			let asig = eAsignaturas[i];
			let inputElement = document.getElementById(`checkbox_${asig.pk}`);
			inputElement.checked = valor;
			console.log(asig.pk, asig.nombre, inputElement);
		}
	};

	const changetypeval2 = async (event) => {
		valor = event.target.checked;

		//		let inputElement1 = document.getElementById("id_firmararchivo");
		let inputfirma = document.getElementById('id_div_password');
		let inputsolicitud = document.getElementById('id_div_solicitud');
		let inputsolicitudsign = document.getElementById('id_div_solicitudsign');

		if (valor == true) {
			inputfirma.style.display = 'none';
			inputsolicitud.style.display = 'none';
			inputsolicitudsign.style.display = '';
		} else {
			inputfirma.style.display = '';
			inputsolicitud.style.display = '';
			inputsolicitudsign.style.display = 'none';
		}
	};

	const generarsolicitudhomologacion = async () => {
		//		loading.setLoading(true, 'Cargando, espere por favor...');
		let a = 0;
		let listaasi = [];
		let listanoasi = [];
		for (let i = 0; i < eAsignaturas.length; i++) {
			let asig = eAsignaturas[i];
			let inputElement = document.getElementById(`checkbox_${asig.pk}`);

			if (inputElement.checked == true) {
				listaasi.push(asig.pk);
				a++;
			} else {
				listanoasi.push(asig.pk);
			}
			console.log(a, listaasi);
		}
		if (solicitud_actual && solicitud_actual.tiene_pago == 'SI') {
			const mensaje4 = {
				title: `NOTIFICACIÓN`,
				html: `No puede volver a generar el archivo debido a que ya ha realizado el pago del valor generado`,
				type: 'info',
				icon: 'info',
				showCancelButton: true,
				showConfirmButton: false,
				allowOutsideClick: false,
				cancelButtonColor: '#E99B40',
				cancelButtonText: 'Cerrar'
			};

			Swal.fire(mensaje4);
		} else if (solicitud_actual && solicitud_actual.firmadoec) {
			const mensaje5 = {
				title: `NOTIFICACIÓN`,
				html: `No puede volver a generar el archivo debido a que ya firmado el arhcivo de solicitud y este ha sido validado.`,
				type: 'info',
				icon: 'info',
				showCancelButton: true,
				showConfirmButton: false,
				allowOutsideClick: false,
				cancelButtonColor: '#E99B40',
				cancelButtonText: 'Cerrar'
			};

			Swal.fire(mensaje5);
		} else {
			if (a == 0) {
//				console.log(solicitud_actual.firmadoec)
				const mensaje = {
					title: `NOTIFICACIÓN`,
					html: `Por favor, seleccione al menos una asignatura a homologar de la maestría para generar la solicitud correctamente.`,
					type: 'info',
					icon: 'info',
					showCancelButton: true,
					showConfirmButton: false,
					allowOutsideClick: false,
					cancelButtonColor: '#E99B40',
					cancelButtonText: 'Cerrar'
				};

				Swal.fire(mensaje);
			} else {
				loading.setLoading(true, 'Cargando, espere por favor...');
				const url = `alumno/secretary/solicitud`;
				const [res, errors] = await apiPOST(fetch, url, {
					action: 'generarsolicitudhomologacion',
					idas: listaasi,
					idnasi: listanoasi
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (errors.length > 0) {
					addToast({
						msg: errors[0].error,
						type: 'error'
					});
				} else {
					if (!res.isSuccess) {
						addToast({
							msg: res.message,
							type: 'error'
						});
					} else {
						if (!res.module_access) {
							if (res.redirect) {
								console.log(res.redirect);
								if (res.token) {
									window.open(`${res.redirect}`, '_blank');
								} else {
									addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
									return;
								}
							} else {
								addToast({
									msg: res.message,
									type: 'warning',
									target: 'newNotificationToast'
								});
							}
						} else {
							const mensajeOtro = {
								title: `NOTIFICACIÓN`,
								html: `Su archivo de solicitud de homologación interna de asignaturas de posgrado ha sido generado correctamente. Por favor, revisarlo y proceder a firmarlo para completar el proceso de solicitud.`,
								type: 'success',
								icon: 'success',
								showCancelButton: false,
								allowOutsideClick: false,
								confirmButtonColor: 'rgb(255, 154, 1)',
								confirmButtonText: `Ver archivo`
							};

							Swal.fire(mensajeOtro).then(async (result) => {
								if (result.value) {
									window.open(`${res.data.reportfile}`, '_blank');
									location.reload();
								}
							});
						}
						loading.setLoading(false, 'Cargando, espere por favor...');
						return;
					}
				}
			}
		}
	};

	const openFirmaSolicitud = async () => {
		limpiarcampos();
		if (solicitud_actual && solicitud_actual.firmadoec == false) {
			loading.setLoading(true, 'Cargando, espere por favor...');
			loading.setLoading(false, 'Cargando, espere por favor...');
			mSizeFirmaSolicitud = 'lg';
			mOpenFirmaSolicitud = true;
			titleFirmaSolicitud = 'Firma de solicitud de homologación';
		} else {
			const mensajeOtro = {
				title: `NOTIFICACIÓN`,
				html: `No puede firmar el archivo de solicitud de homologación puesto que ya ha sido firmado/subido y validado por Secretaría Técnica de Posgrado.`,
				type: 'info',
				icon: 'info',
				showCancelButton: false,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(255, 154, 1)',
				confirmButtonText: `Aceptar`
			};
			Swal.fire(mensajeOtro);
		}
	};

	const limpiarcampos = () => {
		pondFirmaSolicitud;
		pondFirmaSolicitudSign;
		ePassword = '';
	};

	const saveFirmaSolicitud = async (id = null) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmFirmaSolicitud = document.querySelector('#frmFirmaSolicitud');
		const formData = new FormData($frmFirmaSolicitud);

		let inputsolicitudcheck = document.getElementById('id_firmararchivo');

		if (inputsolicitudcheck.checked == true) {
			formData.append('action', 'subirsolicitudhomologacion');
		} else {
			formData.append('action', 'firmarsolicitudhomologacion');
		}

		formData.append('id_soli', solicitud_actual.pk);

		let password = document.getElementById('ePassword');

		if (inputsolicitudcheck.checked == true) {
			let fileDocumentoSign = pondFirmaSolicitudSign.getFiles();
			if (fileDocumentoSign.length == 0) {
				addNotification({
					msg: 'Debe subir el archivo de solicitud firmado con firma electrónica',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			if (fileDocumentoSign.length > 1) {
				addNotification({
					msg: 'Archivo de documento debe ser único',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
			let eFileDocumentoSign = undefined;
			if (pondFirmaSolicitudSign && pondFirmaSolicitudSign.getFiles().length > 0) {
				eFileDocumentoSign = pondFirmaSolicitudSign.getFiles()[0];
			}
			formData.append('eFileSolicitudSignForm', eFileDocumentoSign.file);
		} else {
			if (password.value === null || password.value === undefined || password.value === '') {
				addNotification({
					msg: 'Llene el campo contraseña',
					type: 'error',
					target: 'newNotificationToast'
				});
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}

			let fileDocumento = pondFirmaSolicitud.getFiles();
			if (fileDocumento.length == 0) {
				addNotification({
					msg: 'Debe subir el archivo de su firma electrónica',
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
			if (pondFirmaSolicitud && pondFirmaSolicitud.getFiles().length > 0) {
				eFileDocumento = pondFirmaSolicitud.getFiles()[0];
			}
			formData.append('eFileSolicitudForm', eFileDocumento.file);
		}

		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/secretary/solicitud', formData);
		if (errors.length > 0) {
			addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			if (!res.isSuccess) {
				//				addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
				const mensajeOtro1 = {
					title: `NOTIFICACIÓN`,
					html: `${res.message}`,
					type: 'error',
					icon: 'error',
					showCancelButton: false,
					allowOutsideClick: false,
					confirmButtonColor: 'rgb(255, 154, 1)',
					confirmButtonText: `Aceptar`
				};
				Swal.fire(mensajeOtro1).then(async (result) => {
					if (result.value) {
						mOpenFirmaSolicitud = true;
					}
				});
				if (!res.module_access) {
					goto('/');
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			} else {
				addToast({ type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos' });
				//dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				//				mOpenFirmaSolicitud = false;
				limpiarcampos();
				const mensajeOtro = {
					title: `NOTIFICACIÓN`,
					html: `${res.message}`,
					type: 'info',
					icon: 'info',
					showCancelButton: false,
					allowOutsideClick: false,
					confirmButtonColor: 'rgb(255, 154, 1)',
					confirmButtonText: `Ver archivo firmado`
				};
				Swal.fire(mensajeOtro).then(async (result) => {
					if (result.value) {
						window.open(`${res.data.reportfile}`, '_blank');
						location.reload();
					}
				});
			}
		}
	};

	const payRubros = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const url = `alumno/finanzas`;
		const [res, errors] = await apiPOST(fetch, url, {
			action: 'pay_pending_values',
			id: ePersona.id
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
				if (!res.module_access) {
					if (res.redirect) {
						console.log(res.redirect);
						if (res.token) {
							window.open(`${res.redirect}`, '_blank');
						} else {
							addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
							return;
						}
					} else {
						addNotification({
							msg: res.message,
							type: 'warning',
							target: 'newNotificationToast'
						});
					}
				} else {
					addNotification({
						msg: res.message,
						type: 'warning',
						target: 'newNotificationToast'
					});
				}
				loading.setLoading(false, 'Cargando, espere por favor...');
				return;
			}
		}
	};

	const actionViewDetail = async (id) => {
		/* console.log(eSolicitud);
		console.log(grid);
		grid.forceRender(); */
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/secretary/solicitud', {
			action: 'rubrosgenerados',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (!res.isSuccess) {
			addNotification({
				msg: res.message,
				type: 'error'
			});
		} else {
			console.log(res.data);
			aDataModal = res.data;
			modalDetalleContent = ComponenteRubros;
			mOpenModalGenerico = !mOpenModalGenerico;
			modalTitle = 'Valores generados';
		}
	};

	const downloadsoli = async (eSolicitud) => {
		//		let archivo =  variables.BASE_API + eSolicitud;
		//		console.log(archivo);
		console.log(eSolicitud);
		window.open(eSolicitud, '_blank');
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

	const deletesolicitud = async (id) => {
		if (solicitud_actual.tiene_pago === 'SI') {
			const mensaje3 = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} <b>${
					ePersona.nombre_completo
				}</b> no puede eliminar la solicitud de homologación interna porque ya ha efectuado el pago.`,
				type: 'warning',
				icon: 'warning',
				showCancelButton: false,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(255, 154, 1)',
				confirmButtonText: `Aceptar`
			};
			Swal.fire(mensaje3);
		} else {
			const mensaje2 = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} <b>${
					ePersona.nombre_completo
				}</b> si realiza esta acción, eliminará su solicitud de homologación interna de posgrado, junto con las asignaturas seleccionadas, documentos firmados y valores generados.<br> ¿Está de seguro de realizar esta acción?`,
				type: 'warning',
				icon: 'warning',
				showCancelButton: true,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(255, 154, 1)',
				cancelButtonColor: 'rgb(28, 50, 71)',
				confirmButtonText: `Sí, ${ePersona.sexo_id === 1 ? 'segura' : 'seguro'}`,
				cancelButtonText: 'No, cancelar'
			};
			Swal.fire(mensaje2).then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'deletesolicitud',
							id: id
						},
						'alumno/secretary/solicitud'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								addToast({
									type: 'success',
									header: 'Exitoso!',
									body: 'Su solicitud ha sido eliminada correctamente.'
								});
								location.reload();
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							//addNotification({ msg: error.message, type: 'error' });
							addToast({ type: 'error', header: 'Lo sentimos :(', body: error.message });
						});
				}
			});
		}
	};

	const generatesecondvalue = async (id) => {
		const mensaje4 = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} <b>${
					ePersona.nombre_completo
				}</b> si realiza esta acción, aceptará los resultados de su homologación interna de Posgrado y generará un valor a pagar de <b>$ ${solicitud_actual.costoredondeado}.00</b>. Una vez procesado su pago se realizará la homologación de las asignaturas favorables.`,
				type: 'warning',
				icon: 'warning',
				showCancelButton: true,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(255, 154, 1)',
				cancelButtonColor: 'rgb(28, 50, 71)',
				confirmButtonText: `Sí, ${ePersona.sexo_id === 1 ? 'segura' : 'seguro'}`,
				cancelButtonText: 'No, cancelar'
			};
			
			const mensaje5 = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} <b>${
					ePersona.nombre_completo
				}</b> le comunicamos que aún no puede generar su valor a pagar debido a que sus asiganturas aún no han sido revisadas por el coordinador del programa de maestría.`,
				type: 'warning',
				icon: 'warning',
				showCancelButton: false,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(255, 154, 1)',
				confirmButtonText: `Aceptar`,
			};

			const mensaje6 = {
				title: `NOTIFICACIÓN`,
				html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} <b>${
					ePersona.nombre_completo
				}</b> Su valor a pagar ya ha sido generado. Por favor, de clic en el botón <b>"Pagar rubros"</b>, que lo redireccionará a la pasarela de pagos.`,
				type: 'warning',
				icon: 'warning',
				showCancelButton: false,
				allowOutsideClick: false,
				confirmButtonColor: 'rgb(255, 154, 1)',
				confirmButtonText: `Aceptar`,
			};

		if (solicitud_actual && solicitud_actual.estado == 24) {
			Swal.fire(mensaje4).then(async (result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'generarrubrohomologacion',
							id: solicitud_actual.pk
						},
						'alumno/secretary/solicitud'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								addToast({ type: 'success', header: 'Exitoso!', body: response.value.message });
								grid.forceRender();
								location.reload();
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								//addNotification({ msg: response.value.message, type: 'error' });
								addToast({ type: 'error', header: 'Lo sentimos :(', body: response.value.message });
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							//addNotification({ msg: error.message, type: 'error' });
							addToast({ type: 'error', header: 'Lo sentimos :(', body: error.message });
						});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				//addNotification({ msg: error.message, type: 'error' });
				addToast({ type: 'error', header: 'Lo sentimos :(', body: error.message });
			});

		} else {
			if (solicitud_actual && solicitud_actual.tiene_rubro == "SI") {
				Swal.fire(mensaje6);
			} else {
				Swal.fire(mensaje5);
			}
		}
	};

</script>

<BreadCrumb title="Asignaturas a homologar" items={itemsBreadCrumb} back={backBreadCrumb} />

{#if solicitud_actual && solicitud_actual.estado >= 24}
<div class="row">
	<div class="col-12 text-left">
		<div class="alert alert-success">
			<h4 class="alert-heading"><b>¡Resultados de su homologación!</b></h4>		
			A continuación se detallan los resultados de su solicitud de homologación interna en la tabla <b>"ASIGNATURAS DEL PROGRAMA DE {eCarreraPos.nombrecarrera}"</b>. Se catalogan como "Aplica" aquellas asignaturas que el coordinador del programa consideró apta para homologación, y como "No Aplica" aquellas que no lo son. <br> 
		</div>
	</div>
</div>

<div class="row">
	<div class="col-12 text-left">
		<div class="alert alert-warning">
			Si está de acuerdo con los resultados de su proceso de homologación, haga clic en el <b>botón verde con forma de dólar</b> para generar el valor a pagar. Una vez completado el pago, se aplicará la homologación utilizando las mismas notas que obtuvo en su anterior programa de maestría.
		</div>
	</div>
</div>
{/if}

<div class="row">
	<div class="col-12">
		<div class="card mb-4">
			<div class="card-header">
				<a href="" class="btn btn-warning btn-sm" on:click={() => generarsolicitudhomologacion()}>
					<i class="bi bi-arrow-repeat" /> Generar solicitud</a
				>
				{#if solicitud_actual && solicitud_actual.tiene_rubro == "SI"}
				<a
					href=""
					class="btn btn-success btn-sm text-dark"
					title="Tarjeta o transferencia"
					on:click={() => payRubros()}
				>
					<i class="bi bi-cash-coin" /> Pagar rubros</a
				>
				{/if}

				{#if solicitud_actual}
					<a
						href=""
						class="btn btn-info btn-sm text-dark"
						title=""
						on:click={() => actionViewDetail(solicitud_actual.pk)}
					>
						<i class="bi bi-currency-exchange" /> Valores generados</a
					>
				{/if}
			</div>

			<div class="card-body">
				<div class="table-responsive">
					<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
						<thead class="table-light">
							<tr>
								<th
									scope="col"
									colspan="7"
									class="border-top-0 text-center"
									style="text-align: center;">Solicitud de homologación interna posgrado</th
								>
							</tr>
							<tr>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Código</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Fecha/Hora</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Solicitud/Servicio</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Fecha límite</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Estado</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Archivo</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Acciones</th
								>
							</tr>
						</thead>
						<tbody>
							{#if eSolicitudes.length > 0}
								{#each eSolicitudes as eSolicitud}
									<tr>
										<td class="text-wrap fs-6">
											{eSolicitud.codigo}
										</td>
										<td class="text-wrap fs-6" style="text-align: center;">
											{eSolicitud.fecha}
											{eSolicitud.hora}
										</td>
										<td class="text-wrap fs-6" style="text-align: center;">
											{eSolicitud.descripcion}
										</td>
										<td class="fs-6" style="text-align: center;">
											{eSolicitud.fecha_limite_pago}
										</td>
										<td class="fs-6" style="text-align: center;">
											<span
												class="badge rounded-pill text-dark"
												style={eSolicitud.color_estado_display}
												>{eSolicitud.estado_display}
											</span>
										</td>
										<td class="fs-6" style="text-align: center;">
											{#if eSolicitud.archivo_respuesta}
												<button
													class="btn btn-link btn-sm p-0 m-0"
													on:click|preventDefault={async () =>
														await downloadsoli(eSolicitud.archivo_respuesta)}
												>
													<i
														class="bi bi-download"
														style="font-size: 1.7rem; color: #198754;"
													/></button
												>
											{:else}
												<button
													class="btn btn-link btn-sm p-0 m-0"
													on:click|preventDefault={async () =>
														await downloadsoli(eSolicitud.archivo_solicitud)}
												>
													<i
														class="bi bi-download"
														style="font-size: 1.7rem; color: #198754;"
													/></button
												>
											{/if}
										</td>
										<td class="fs-6" style="text-align: center;">
											<button
												class="btn btn-link btn-sm p-0 m-0"
												on:click={() => openFirmaSolicitud()}
											>
												<i class="bi bi-pencil-square" style="font-size: 1.7rem; color: #3a87ad" />
											</button>
											<button
												class="btn btn-link btn-sm p-0 m-0"
												on:click={() => deletesolicitud(eSolicitud.pk)}
											>
												<i class="bi bi-trash-fill" style="font-size: 1.7rem; color: #dc3545" />
											</button>
											<button
												class="btn btn-link btn-sm p-0 m-0"
												on:click={() => generatesecondvalue(eSolicitud.pk)}
											>
												<i class="bi bi-cash-coin" style="font-size: 1.7rem; color: #19cb98" />
											</button>
										</td>
									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="7" class="text-center">
										NO EXISTEN REGISTROS DE SOLICITUD DE HOMOLOGACIÓN INTERNA</td
									>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>

<div class="row">
	<div class="col-12">
		<div class="card mb-4">
			<div class="card-body">
				<div class="table-responsive">
					<table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
						<thead class="table-light">
							<tr>
								<th
									scope="col"
									colspan="6"
									class="border-top-0 text-center"
									style="text-align: center;">ASIGNATURAS DEL PROGRAMA DE {eCarreraPos.nombrecarrera}</th
								>
							</tr>
							<tr>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;">N°</th>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Asignatura</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Detalle de horas</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Créditos</th
								>
								{#if solicitud_actual && solicitud_actual.visible}
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Nota</th
								>
								{/if}
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>Estado</th
								>
								<th scope="col" class="border-top-0 text-center" style="text-align: center;"
									>¿Homologar?<br />
									<input
										type="checkbox"
										class="form-check-input"
										id="id_todos"
										on:change={changetypeval}
									/>
									<label class="form-check-label" for="id_todos" />
								</th>
							</tr>
						</thead>
						<tbody>
							{#if eAsignaturas.length > 0}
								{#each eAsignaturas as eAsignatura, num}
									<tr>
										<td class="text-wrap fs-6">
											{num + 1}
										</td>
										<td class="text-wrap fs-6" style="text-align: center;">
											<b>{eAsignatura.nombre}</b>
										</td>
										<td class="fs-6" style="text-align: center;">
											<span
												class="badge rounded-pill bg-success"
												title="Total Horas Aprendizaje Contacto Docente"
												>{eAsignatura.horasacdtotal}</span
											>
											<span
												class="badge rounded-pill bg-warning"
												title="Total Horas Aprendizaje Prático Experimental"
												>{eAsignatura.horasapetotal}</span
											>
											<span
												class="badge rounded-pill bg-danger"
												title="Total Horas Aprendizaje Autónomo">{eAsignatura.horasautonomas}</span
											>
											<span class="badge rounded-pill bg-primary" title="Total Horas"
												>{eAsignatura.horas}</span
											>
										</td>
										<td class="fs-6" style="text-align: center;">
											{eAsignatura.creditos}
										</td>
										{#if solicitud_actual && solicitud_actual.visible}
											<td class="fs-6" style="text-align: center;">
												{eAsignatura.nota}
											</td>
										{/if}		
										<td class="fs-6" style="text-align: center;">
											{#if eAsignatura.color === '0'}
												<span
													class="badge rounded-pill text-dark"
													style="color: #3a87ad!important; font-weight: bold; font-size:12px"
													>{eAsignatura.estado}</span
												>
											{:else}
												<span class="badge rounded-pill text-dark" style={eAsignatura.color}
													>{eAsignatura.estado}
												</span>
											{/if}
										</td>
										<td class="fs-6" style="text-align: center;">
											{#if solicitud_actual && (solicitud_actual.tiene_pago === "SI" || solicitud_actual.firmadoec)}
												<input
													type="checkbox"
													class="form-check-input"
													id={`checkbox_${eAsignatura.pk}`} disabled
												/>
											{:else}
												<input
													type="checkbox"
													class="form-check-input"
													id={`checkbox_${eAsignatura.pk}`}
												/>
											{/if}
											<label class="form-check-label" for={`checkbox_${eAsignatura.pk}`} />
											<!---											{eAsignatura.pk}-->
										</td>
									</tr>
								{/each}
							{:else}
								<tr>
									<td colspan="8" class="text-center"
										>NO EXISTEN ASIGNATURAS CONFIGURADAS EN LA MALLA DE ESTA CARRERA</td
									>
								</tr>
							{/if}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
</div>

<Modal
	isOpen={mOpenFirmaSolicitud}
	toggle={mToggleFirmaSolicitud}
	size={mSizeFirmaSolicitud}
	class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
	backdrop="static"
	fade={false}
>
	<ModalHeader toggle={mToggleFirmaSolicitud}>
		<h4>{titleFirmaSolicitud}</h4>
	</ModalHeader>
	<ModalBody>
		<form
			id="frmFirmaSolicitud"
			on:submit|preventDefault={() => saveFirmaSolicitud(solicitud_actual.pk)}
			autocomplete="off"
		>
			<div class="card-body">
				<div class="row g-3">
					{#if solicitud_actual.archivo_solicitud}
						<button
							class="btn btn-link btn-sm p-0 m-0"
							on:click|preventDefault={async () =>
								await downloadsoli(solicitud_actual.archivo_solicitud)}
						>
							Click aquí para descargar el archivo de solicitud de homologación interna generado</button
						>
					{/if}
					<div class="col-md-12">
						<input
							type="checkbox"
							class="form-check-input"
							id="id_firmararchivo"
							on:change={changetypeval2}
						/>
						<label class="form-check-label" for="id_firmararchivo" />
						<b
							>Marque esta casilla si no tiene firma electrónica, para subir directamente el archivo
							firmado.</b
						><br />
					</div>
					<div class="col-md-12" id="id_div_solicitud">
						<label for="eFileSolicitudForm" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Archivo de firma ec:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eFileSolicitudForm"
							bind:this={pondFirmaSolicitud}
							{nameFirmaSolicitud}
							name="eFileSolicitudForm"
							labelIdle={[
								'<span class="filepond--label-action">Subir archivo de firma electrónica</span>'
							]}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileFirmaSolicitud}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxFileSize="10MB"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 10Mb</small>
					</div>
					<div class="col-md-12" id="id_div_password">
						<label for="ePassword" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Contraseña:
						</label>
						<input
							type="password"
							class="form-control"
							id="ePassword"
							name="ePassword"
							bind:value={ePassword}
						/>
					</div>

					<div class="col-md-12" id="id_div_solicitudsign" style="display: none;">
						<label for="eFileSolicitudSignForm" class="form-label fw-bold"
							><i
								title="Campo obligatorio"
								class="bi bi-exclamation-circle-fill"
								style="color: red"
							/> Archivo de solicitud firmado por el inscrito:</label
						>
						<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
						<FilePond
							class="pb-0 mb-0"
							id="eFileSolicitudSignForm"
							bind:this={pondFirmaSolicitudSign}
							{nameFirmaSolicitudSign}
							name="eFileSolicitudSignForm"
							labelIdle={['<span class="filepond--label-action">Subir archivo de firmado</span>']}
							allowMultiple={true}
							oninit={handleInit}
							onaddfile={handleAddFileFirmaSolicitudSign}
							credits=""
							acceptedFileTypes={['application/pdf']}
							labelInvalidField="El campo contiene archivos no válidos"
							maxFiles="1"
							maxFileSize="10MB"
							maxParallelUploads="1"
						/>
						<small class="text-warning">Tamaño máximo permitido 10Mb. Formato permitido: pdf</small
						><br />
						<small class="text-warning"
							>Recuerde que el archivo de solicitud de homologación debe ser firmado por el
							inscrito, caso contrario no se podrá proceder con su proceso de homologación.</small
						>
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info"
						style="background-color: #FF9A01; border-color: #FF9A01">Guardar</button>
						<a
							href=""
							class="btn btn-danger"
							style="background-color: #13344B; border-color: #13344B"
							on:click={() => closeFirmaSolicitudForm()}>Cerrar</a
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
		aData={aDataModal}
		size={modalSize}
	/>
{/if}

<style global>
	@import 'filepond/dist/filepond.css';
	@import 'filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css';
	@import 'filepond-plugin-image-edit/dist/filepond-plugin-image-edit.css';
	.filepond--drop-label {
		border-radius: 0.75rem;
		color: #ffffff;
		background: #1f2531 !important;
		box-shadow: 0 0.1875rem 0.625rem rgb(0 0 0 / 15%) !important;
	}
</style>
