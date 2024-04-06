<script lang="ts">
	import { apiGET, apiPOST, browserGet, changeProfile, logOutUser } from '$lib/utils/requestUtils';
	import { variables } from '$lib/utils/constants';
	import { addToast } from '$lib/store/toastStore';
	import { afterUpdate, onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
	import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader, Spinner } from 'sveltestrap';
	import { loading } from '$lib/store/loadingStore';
	import Swal from 'sweetalert2';
	import { addNotification } from '$lib/store/notificationStore';
	import { goto } from '$app/navigation';
	import DetalleValoresPendientes from '$components/Alumno/Matricula/DetalleValoresPendientes.svelte';
	const DEBUG = import.meta.env.DEV;
	let itemsBreadCrumb = [{ text: 'Matriculación', active: true, href: undefined }];
	let backBreadCrumb = { href: '/', text: 'Atrás' };
	let load = true;
	let Title = 'Automatriculación Online';
	let ePersona = undefined;
	let eInscripcion = undefined;
	let eCarrera = undefined;
	let eMalla = undefined;
	let FichaSocioEconomicaINEC = undefined;
	let ePeriodoMatricula = undefined;
	let ePeriodo = undefined;
	let eInscripcionMalla = undefined;
	let eNivelMalla = undefined;
	let eMatricula = undefined;
	let eMateriasAsignadas = [];
	let perdida_gratuidad = false;
	let valorMatricula = 0.0;
	let valorArancel = 0.0;
	let valorTotal = 0.0;
	let mensaje_gratuidad = '';
	let mensajeConfirmarDiferido = '';
	let periodo_id_aux = 0;
	let acept_t = false;
	let mSizeConfirmarMatricula = 'lg';
	let mOpenConfirmarMatricula = false;
	const mToggleConfirmarMatricula = () => (mOpenConfirmarMatricula = !mOpenConfirmarMatricula);
	let mSizeRubro = 'xl';
	let mOpenRubro = false;
	let aMateriaAsignadas = [];
	const mToggleRubro = () => (mOpenRubro = !mOpenRubro);
	let mOpenConfirmarDiferido = false;
	let matricula_id = 0;
	let tiene_valores_pendientes = false;
	let msg_valores_pendientes = '';
	let tipo_valores_alerta = '';
	const mToggleConfirmarDiferido = () => (mOpenConfirmarDiferido = !mOpenConfirmarDiferido);
	let aDataModal = {};
	let mOpenModal = false;
	let mTitleModal = '';
	let mClass =
		'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-xl-down';
	let modalContent;
	let mSize = 'xl';
	const mToggleModal = () => (mOpenModal = !mOpenModal);
	export let aData;
	onMount(async () => {
		if (aData !== undefined) {
			load = false;
			Title = aData.Title;
			ePersona = aData.ePersona;
			eInscripcion = aData.eInscripcion;
			eCarrera = aData.eCarrera;
			eMalla = aData.eMalla;
			FichaSocioEconomicaINEC = aData.FichaSocioEconomicaINEC;
			ePeriodoMatricula = aData.ePeriodoMatricula;
			ePeriodo = ePeriodoMatricula.periodo;
			eInscripcionMalla = aData.eInscripcionMalla;
			eNivelMalla = aData.eNivelMalla;
			eMatricula = aData.eMatricula;
			eMateriasAsignadas = aData.eMateriasAsignadas;
			valorMatricula = aData.valorMatricula;
			valorArancel = aData.valorArancel;
			valorTotal = aData.valorTotal;
			tiene_valores_pendientes = aData.tiene_valores_pendientes ?? false;
			msg_valores_pendientes = aData.msg_valores_pendientes ?? '';
			tipo_valores_alerta = aData.tipo_valores_alerta ?? '';
		}
		load = false;
	});

	afterUpdate(async () => {
		/*const elementActionViewPendingValues = document.getElementById('btnVerRubros');
		console.log('element: ', elementActionViewPendingValues);
		if (elementActionViewPendingValues) {
			elementActionViewPendingValues.addEventListener('click', viewDetailRubros);
		}*/
	});

	const actionRun = (event) => {
		//console.log(event.detail);
	};

	const viewDetailRubros = async () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const url = `alumno/general/data`;
		const [res, errors] = await apiPOST(fetch, url, {
			action: 'detail_pending_values',
			id: eMatricula.nivel_id
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
				//console.log(res.data);
				aDataModal = res.data;
				modalContent = DetalleValoresPendientes;
				mClass =
					'modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down';
				mOpenModal = !mOpenModal;
				mTitleModal = 'Detalle de valores pendientes';
				mSize = 'xl';
			}
		}
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

	const closeConfirmarMatricula = () => {
		acept_t = false;
		mOpenConfirmarMatricula = false;
	};

	const closeRubro = () => {
		mOpenRubro = false;
	};

	const openConfirmarMatricula = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (ePeriodoMatricula.valida_terminos) {
			mSizeConfirmarMatricula = 'xl';
		} else {
			mSizeConfirmarMatricula = 'sm';
		}
		mOpenConfirmarMatricula = true;
	};

	const openRubros = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'loadDetalleRubros',
				id: eMatricula.id
			},
			'alumno/matricula/pregrado'
		)
			.then((response) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (response.value.isSuccess) {
					const aData = response.value.data;
					mSizeRubro = 'xl';
					mOpenRubro = true;
					aMateriaAsignadas = [...aData];
				} else {
					loading.setLoading(false, 'Cargando, espere por favor...');
					addNotification({ msg: response.value.message, type: 'error' });
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const confirmarMatricula = () => {
		const acepto_terminos = acept_t;
		if (!acepto_terminos && ePeriodoMatricula.valida_terminos) {
			addNotification({
				msg: `Para continuar, por favor acepte los términos y condiciones.`,
				type: 'warning',
				target: 'newNotificationToast'
			});
			return false;
		}
		const _acept_t = acepto_terminos ? 1 : 0;
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, </br><b>¿Está ${ePersona.es_mujer ? 'segura' : 'seguro'} de aceptar la matrícula?</b>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: 'rgb(25, 135, 84)',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Sí, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'aceptarAutomatricula',
							id: eInscripcion.id,
							termino: _acept_t
						},
						'alumno/matricula/pregrado'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							mOpenConfirmarMatricula = false;
							if (response.value.isSuccess) {
								matricula_id = response.value.data.phase;
								if (
									ePeriodoMatricula.valida_cuotas_rubro &&
									ePeriodoMatricula.num_cuotas_rubro &&
									response.value.data.valorarancel >= ePeriodoMatricula.monto_rubro_cuotas
								) {
									openConfirmarDiferir(response.value.data);
									closeConfirmarMatricula();
								} else {
									const mensaje = {
										title: `¡MATRICULACIÓN EXITOSA!`,
										html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
											ePersona.nombre_completo
										}, le informamos que el proceso de aceptación de matrícula ha finalizado.`,
										type: 'success',
										icon: 'success',
										showCancelButton: false,
										allowOutsideClick: false,
										confirmButtonColor: '#3085d6',
										cancelButtonColor: '#d33',
										confirmButtonText: 'Aceptar',
										cancelButtonText: 'Cancelar'
									};
									Swal.fire(mensaje)
										.then((result) => {
											if (result.value) {
												goto('/');
											}
										})
										.catch((error) => {
											loading.setLoading(false, 'Cargando, espere por favor...');
											addNotification({ msg: error.message, type: 'error' });
										});
								}
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({ msg: response.value.message, type: 'error' });
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({ msg: error.message, type: 'error' });
						});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const rechazarMatricula = () => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, con esta acción usted estará liberando un cupo. </br><b>¿Está ${
				ePersona.es_mujer ? 'segura' : 'seguro'
			} de rechazar la matrícula?</b>`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: true,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Sí, seguro',
			cancelButtonText: 'No, cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'rechazoAutomatricula',
							id: eInscripcion.id
						},
						'alumno/matricula/pregrado'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								const mensaje = {
									title: `NOTIFICACIÓN`,
									html: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
										ePersona.nombre_completo
									}, le informamos que el proceso de aceptación de matrícula ha finalizado.`,
									type: 'success',
									icon: 'success',
									showCancelButton: false,
									allowOutsideClick: false,
									confirmButtonColor: '#3085d6',
									cancelButtonColor: '#d33',
									confirmButtonText: 'Aceptar',
									cancelButtonText: 'Cancelar'
								};
								Swal.fire(mensaje)
									.then((result) => {
										if (result.value) {
											logOutUser();
										}
									})
									.catch((error) => {
										loading.setLoading(false, 'Cargando, espere por favor...');
										addNotification({ msg: error.message, type: 'error' });
									});
							} else {
								loading.setLoading(false, 'Cargando, espere por favor...');
								addNotification({ msg: response.value.message, type: 'error' });
							}
						})
						.catch((error) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							addNotification({ msg: error.message, type: 'error' });
						});
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const openConfirmarDiferir = (data) => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		periodo_id_aux = data.periodo_id;
		mOpenConfirmarDiferido = true;
		mensajeConfirmarDiferido = `<p style="font-size:15px !important">${
			ePersona.es_mujer ? 'Estimada' : 'Estimado'
		} ${ePersona.nombre_completo}, ¿desea diferir el valor de <strong>$ ${
			data.valorarancel
		}</strong> del rubro <strong>${data.descripcionarancel}</strong> a <strong>${
			ePeriodoMatricula.num_cuotas_rubro
		}</strong> ${ePeriodoMatricula.num_cuotas_rubro > 1 ? 'meses' : 'mes'}?</p>
		${
			ePeriodoMatricula.valida_rubro_acta_compromiso
				? '<h4>Recordatorio</h4><p>Al final del proceso se generará una acta de compromiso</p>'
				: ''
		}`;

		/*$(".modal-body", self.$modalConfirmarDiferir).html(`<p style="font-size:15px !important">{% if persona.sexo.id == 1 %}Estimada{% else %}Estimado{% endif %} {{ persona }}, ¿desea diferir el valor de <strong>$ ${data.aData.valorarancel}</strong> del rubro <strong>${data.aData.descripcionarancel}</strong> a <strong>${self.num_cuotas_rubro}</strong> ${self.num_cuotas_rubro > 1 ? 'meses':'mes' }?</p>`);
                    self.$modalConfirmarDiferir.modal({backdrop:'static', width: '50%'}).modal('show');*/
	};

	const confirmarDiferir = () => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		loadAjax(
			{
				action: 'to_differ',
				idm: matricula_id
			},
			'alumno/matricula/pregrado'
		)
			.then((response) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				if (response.value.isSuccess) {
					const mensaje = {
						title: `NOTIFICACIÓN`,
						html: `<p>${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
							ePersona.nombre_completo
						}, le informamos que se procedió a diferir los rubros generados. El proceso de matriculación ha finalizado.<p>
						<p>Consulte los valores en Módulo "Mis Finanzas"</p>
						${
							response.value.data.acta_compromiso && ePeriodoMatricula.valida_rubro_acta_compromiso
								? "<p>Descargar <a class='btn btn-link' href='" +
								  response.value.data.acta_compromiso +
								  "' target='_blank'>Acta de Compromiso</a></p>"
								: ''
						}`,
						type: 'success',
						icon: 'success',
						showCancelButton: false,
						allowOutsideClick: false,
						confirmButtonColor: '#3085d6',
						cancelButtonColor: '#d33',
						confirmButtonText: 'Aceptar',
						cancelButtonText: 'Cancelar'
					};
					Swal.fire(mensaje)
						.then((result) => {
							if (result.value) {
								loading.setLoading(true, 'Cargando, espere por favor...');
								if (ePeriodoMatricula.valida_login) {
									logOutUser();
								} else {
									changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
								}
							} else {
								loading.setLoading(true, 'Cargando, espere por favor...');
								if (ePeriodoMatricula.valida_login) {
									logOutUser();
								} else {
									changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
								}
							}
						})
						.catch((error) => {
							addNotification({ msg: error.message, type: 'error' });
						});
				} else {
					addNotification({ msg: response.value.message, type: 'error' });
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				addNotification({ msg: error.message, type: 'error' });
			});
	};

	const closeConfirmarDiferir = () => {
		mOpenConfirmarDiferido = false;
		const mensaje = {
			title: `NOTIFICACIÓN`,
			text: `${ePersona.es_mujer ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, se informa que el proceso ha finalizado y registra valores por concepto de matricula. Consulte los valores en Módulo "Mis Finanzas"`,
			type: 'warning',
			icon: 'warning',
			showCancelButton: false,
			allowOutsideClick: false,
			confirmButtonColor: '#3085d6',
			cancelButtonColor: '#d33',
			confirmButtonText: 'Aceptar',
			cancelButtonText: 'Cancelar'
		};
		Swal.fire(mensaje)
			.then((result) => {
				if (result.value) {
					loading.setLoading(true, 'Cargando, espere por favor...');

					if (ePeriodoMatricula.valida_login) {
						logOutUser();
					} else {
						changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
					}
				} else {
					loading.setLoading(true, 'Cargando, espere por favor...');
					if (ePeriodoMatricula.valida_login) {
						logOutUser();
					} else {
						changeProfile('token/change/academic_period', { periodo_id: periodo_id_aux }, 1);
					}
				}
			})
			.catch((error) => {
				loading.setLoading(false, 'Cargando, espere por favor...');
				/*addToast({
					type: 'error',
					header: 'Ocurrio un error',
					body: error.message
				});*/
				addNotification({ msg: error.message, type: 'error' });
			});
	};
</script>

<svelte:head>
	<title>{Title}</title>
</svelte:head>

{#if !load}
	<BreadCrumb title={Title} items={itemsBreadCrumb} back={backBreadCrumb} />
	<div class="row mb-3">
		<div
			class={eInscripcion && eInscripcion.tiene_perdida_gratuidad
				? 'col-xl-8 col-lg-8 col-md-12 col-12'
				: 'col-12'}
		>
			<!--<div
				class="pt-16 rounded-top-md"
				style="background: url({variables.BASE_API_STATIC}/images/aok/banner-tarjeta3.png) no-repeat; background-size: cover;"
			/>-->
			<div
				class="d-flex align-items-end justify-content-between bg-white px-4 pt-4 pb-4 rounded-3 rounded-bottom-md shadow-sm h-100"
			>
				<div class="d-flex align-items-center">
					<div
						class="me-4 position-relative d-flex justify-content-end align-items-end mt-n5 d-none d-sm-block d-sm-none d-md-block"
					>
						<img
							src={ePersona.foto_perfil}
							onerror="this.onerror=null;this.src='./image.png'"
							class="avatar-xxl rounded-circle border border-4 border-white"
						/>
						<a
							href="#"
							class="position-absolute mt-2 ms-n3"
							data-bs-toggle="tooltip"
							data-placement="top"
							title="Verifed"
						>
							<img src="./assets/images/svg/checked-mark.svg" alt="" height="35" width="35" />
						</a>
					</div>
					<div class="lh-1">
						<h2 class="mb-2">{ePersona.nombre_completo}</h2>
						<p class="mb-2 d-block lh-lg">
							{#if ePersona.emailinst !== ePersona.email}
								{#if ePersona.emailinst}
									<b>Correo institucional:</b> {DEBUG ? 'unemi@unemi.edu.ec' : ePersona.emailinst}
								{/if}
								{#if ePersona.email}
									<b>Correo personal:</b> {DEBUG ? 'unemi@unemi.edu.ec' : ePersona.email}
								{/if}
							{:else}
								<b>Correo institucional:</b> {DEBUG ? 'unemi@unemi.edu.ec' : ePersona.emailinst}
							{/if}
							<b>Teléfono:</b>
							{DEBUG ? '0920991910' : ePersona.telefono}
						</p>
						<p class="mb-2 d-block lh-lg">
							<b>Ciudad:</b>
							{DEBUG ? 'MILAGRO' : ePersona.ciudad} <b>Dirección:</b>
							{DEBUG ? 'cdla. Universitaria Romulo Minchala' : ePersona.direccion}
						</p>
						<p class="mb-2 d-block lh-lg">
							<b>Carrera:</b>
							{eCarrera.display} <b>Malla:</b>
							{eMalla.display}
						</p>
						<p class="mb-2 d-block lh-lg">
							<b>Periodo:</b>
							{ePeriodo.display}
						</p>
						<p class="mb-2 d-block lh-lg">
							{#if FichaSocioEconomicaINEC}
								<b>Grupo socioeconómico:</b>
								<span
									class="badge bg-info text-white"
									style="width: 6rem; background-color: #04c !important;"
									>{FichaSocioEconomicaINEC}</span
								>{/if} <b>Nivel de malla:</b>
							{eNivelMalla.nombre}
						</p>
					</div>
				</div>
			</div>
		</div>
		{#if eInscripcion && eInscripcion.tiene_perdida_gratuidad}
			<div class="col-xl-4 col-lg-4 col-md-12 col-12 mt-0 mt-sm-2 mt-md-2 mt-lg-0">
				<div class="card h-100 ">
					<div class="d-lg-flex justify-content-between align-items-center card-header">
						<div class="mb-3 mb-lg-0">
							<h3 class="mb-0">Registra perdida de gratuidad</h3>
							<span>Motivos por perdida de gratuidad</span>
						</div>
					</div>
					<div class="card-body">
						<ul class="list-group border-0">
							{#if eInscripcion.motivos_perdida_gratuidad.length > 0}
								{#each eInscripcion.motivos_perdida_gratuidad as motivos}
									<li
										class="list-group-item d-flex justify-content-start align-items-center border-0 fs-6 m-0 p-1"
									>
										<i class="fe fe-alert-octagon text-warning me-2" />
										{motivos}
									</li>
								{/each}
							{:else}
								<li class="list-group-item border-0">
									<i class="fe fe-alert-octagon text-warning" /> Reportado por la SENESCYT
								</li>
							{/if}
						</ul>
					</div>
				</div>
			</div>
		{/if}
	</div>
	{#if ePeriodoMatricula.valida_deuda && tiene_valores_pendientes}
		<div class="row mb-3">
			<div class="col-12">
				<div class="alert alert-{tipo_valores_alerta ?? 'warning'}">
					{@html msg_valores_pendientes}
					{#if ePeriodoMatricula.ver_deduda}
						<button
							on:click={viewDetailRubros}
							class="btn btn-primary rounded-5 btn-sm btn-cian-opacity"
						>
							Ver deuda
						</button>
					{/if}
				</div>
			</div>
		</div>
	{/if}
	{#if valorTotal > 0}
		<div class="row mb-3">
			{#if eMatricula.gratuidad == 2 || eMatricula.gratuidad == 3}
				<div class="col-xl-8 col-lg-8 col-md-12 col-12 ">
					<div class="alert alert-warning m-0 h-100" role="alert">
						<h4 class="alert-heading">Observación</h4>
						{#if eMatricula.gratuidad == 2}
							<p class="">
								Con base al Art.5 del Reglamento para garantizar el cumplimiento de la gratuidad
								emitido por el Concejo de Educaci&oacute;n Superior (CES) y en relaci&oacute;n a los
								Arts. 6, 7 y 12 del Reglamento interno para garantizar el ejercicio del derecho a la
								gratuidad en la Universidad Estatal de Milagro. Su estado es P&Eacute;RDIDA PARCIAL
								DE LA GRATUIDAD y tendr&aacute; que cancelar el valor correspondiente entre
								matr&iacute;cula y arancel.
							</p>
						{:else if eMatricula.gratuidad == 3}
							{#if ePersona.tiene_otro_titulo}
								<p class="">
									De acuerdo al contenido de la Matriz de Tercer Nivel remitida por la Secretaría de
									Educación, Ciencia, Tecnología e Innovación SENESCYT a nuestra IES, en
									concordancia con lo estipulado en el artículo 63 del Reglamento del SNNA y en la
									Disposición General Séptima del Reglamento de Régimen Académico, se informa que
									usted, actualmente, se encuentra SIN GRATUIDAD en la educación superior pública;
									motivo por el cual deberá cancelar los valores correspondientes, durante el
									desarrollo de su carrera universitaria.
								</p>
								<p class="text-wrap p-0 m-0">
									Estimad{ePersona.es_mujer ? 'a' : 'o'} estudiante registra título en otra IES Pública.
									Su estado es de pérdida total de la gratuidad. Debe cancelar por todas las asignaturas.
								</p>
							{:else if eInscripcion.tiene_perdida_gratuidad}
								<p class="text-wrap p-0 m-0">
									De acuerdo al contenido de la Matriz de Tercer Nivel remitida por la Secretaría de
									Educación, Ciencia, Tecnología e Innovación SENESCYT a nuestra IES, en
									concordancia con lo estipulado en el artículo 63 del Reglamento del SNNA y en la
									Disposición General Séptima del Reglamento de Régimen Académico, se informa que
									usted, actualmente, se encuentra SIN GRATUIDAD en la educación superior pública;
									motivo por el cual deberá cancelar los valores correspondientes, durante el
									desarrollo de su carrera universitaria.
								</p>
								<p class="text-wrap p-0 m-0">
									Estimad{ePersona.es_mujer ? 'a' : 'o'} estudiante registra perdida de gratuidad reportado
									por la SENESCYT. Su estado es de pérdida total de la gratuidad. Debe cancelar por todas
									las asignaturas.
								</p>
							{:else}
								<p class="text-wrap p-0 m-0">
									Con base al Art.11 del Reglamento para garantizar el cumplimiento de la gratuidad
									emitido por el Concejo de Educaci&oacute;n Superior (CES) y en relaci&oacute;n al
									Art.11 del Reglamento interno para garantizar el ejercicio del derecho a la
									gratuidad en la Universidad Estatal de Milagro. Usted supera el 30% de las
									asignaturas reprobadas correspondientes al plan de estudios como indica la Ley. Su
									estado es P&Eacute;RDIDA DEFINITIVA DE LA GRATUIDAD. A partir de este momento
									todas las asignaturas, cursos o sus equivalentes hasta la culminaci&oacute;n de su
									carrera, cancelar&aacute; los valores respectivos a matr&iacute;culas y aranceles.
								</p>
							{/if}
						{/if}
					</div>
				</div>
			{/if}
			<div
				class={eMatricula.gratuidad == 2 || eMatricula.gratuidad == 3
					? 'col-xl-4 col-lg-4 col-md-12 col-12 mt-0 mt-sm-2 mt-md-2 mt-lg-0'
					: 'col-12'}
			>
				<div class="card h-100">
					<div class="d-flex justify-content-between align-items-center card-header">
						<div class="mb-3 mb-lg-0">
							<h5 class="mb-0">Rubros generados</h5>
						</div>
						<button class="btn btn-primary rounded-5 btn-sm btn-cian-opacity" on:click={openRubros}>
							<i class="fe fe-eye" />
						</button>
					</div>

					<!-- Table -->
					<div class="card-body">
						<ul class="list-group list-group-flush">
							<li
								class="list-group-item px-0 d-flex justify-content-between fs-6 text-dark fw-medium pt-0"
							>
								<span>Valor de matrícula (USD):</span>
								<span>${valorMatricula}</span>
							</li>
							<li
								class="list-group-item px-0 d-flex justify-content-between fs-6 text-dark fw-medium pb-0"
							>
								<span>Total de arancel (USD):</span>
								<span>${valorArancel}</span>
							</li>
						</ul>
					</div>
					<div class="card-footer">
						<div class="px-0 d-flex justify-content-between fs-5 text-dark fw-semibold">
							<span>Total a pagar (USD)</span>
							<span>${valorTotal}</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
	<div class="row">
		<div class="col-12">
			<div class="card">
				<div class="d-lg-flex justify-content-between align-items-center card-header">
					<div class="mb-3 mb-lg-0">
						<h4 class="mb-0">Asignaturas por confirmar</h4>
					</div>
					<div class="d-lg-flex justify-content-between align-items-center">
						{#if ePeriodoMatricula.bloquea_por_deuda && tiene_valores_pendientes}
							<span class="text-warning fw-bold">Bloqueo por valores pendientes</span>
						{:else}
							<button
								class="btn btn-success btn-sm me-2"
								type="button"
								on:click={() => openConfirmarMatricula()}>CONFIRMAR MATRÍCULA</button
							>
							<button
								class="btn btn-danger btn-sm mt-sm-0 mt-2"
								type="button"
								on:click={() => rechazarMatricula()}>RECHAZAR MATRÍCULA</button
							>
						{/if}
					</div>
				</div>

				<!-- Table -->
				<div class="card-body m-0 p-0">
					<div class="table-responsive scrollbar">
						<table class="table table_primary tabla_responsive  m-0 p-0">
							<thead class="table-light">
								<tr>
									<th class="text-center" scope="row">#</th>
									<!--<th class="border-0">Carrera</th>-->
									<th class="text-center">Asignatura</th>
									<th class="text-center">Nivel</th>
									<th class="text-center">Paralelo</th>
									<th class="text-center">Sección</th>
								</tr>
							</thead>
							<tbody class="list">
								{#each eMateriasAsignadas as eMateriaAsignada, i}
									<tr
										class="accordion-toggle collapsed"
										id="accordion1"
										data-bs-toggle="collapse"
										data-bs-parent="#accordion1"
										data-bs-target="#collapseOne"
									>
										<td scope="row" class="align-middle border-top-0 text-center">
											{i + 1}
										</td>
										<!--<td class="align-middle border-top-0">
							{eMateriaAsignada.matricula.inscripcion.carrera.nombre}
						</td>-->
										<td class="align-middle border-top-0">
											{eMateriaAsignada.materia.asignaturamalla.asignatura.nombre}
										</td>
										<td class="align-middle border-top-0 text-center">
											{eMateriaAsignada.materia.asignaturamalla.nivelmalla.nombre}
										</td>
										<td class="align-middle border-top-0 text-center">
											{eMateriaAsignada.materia.paralelomateria.nombre}
										</td>
										<td class="align-middle border-top-0 text-center">
											{eMateriaAsignada.matricula.inscripcion.sesion.nombre}
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
	</div>
	<Modal
		isOpen={mOpenConfirmarMatricula}
		toggle={mToggleConfirmarMatricula}
		size={mSizeConfirmarMatricula}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={mToggleConfirmarMatricula}>
			<h4>Confirmar matrícula</h4>
		</ModalHeader>
		<ModalBody>
			<!--{#if perdida_gratuidad}
				<div class="alert alert-danger" role="alert">
					<p>{@html mensaje_gratuidad}</p>
					<hr />
					<p class="mb-0">
						Una vez confirmada la matriculación, podrá consultar los rubros a pagar a través del
						módulo "Mis Finanzas".
					</p>
				</div>
			{/if}-->
			{#if ePeriodoMatricula.valida_terminos}
				<div class="p-4">
					<h4 style="color: red; " class="text-center">
						<strong>TÉRMINOS Y CONDICIONES</strong>
					</h4>
					<div class="terminos mt-4">
						{@html ePeriodoMatricula.terminos}
					</div>
				</div>
			{/if}
			<p>
				{ePersona.es_mujer ? 'Estimada' : 'Estimado'}
				{ePersona.nombre_completo}, al confirmar usted estará aceptando (<b
					>{eMateriasAsignadas.length}</b
				>) {eMateriasAsignadas.length > 1 ? 'materias' : 'materia'}.
				<!--<b class="fs-5">¿Está {ePersona.es_mujer ? 'segura' : 'seguro'} de aceptar la matrícula?</b>-->
			</p>
		</ModalBody>
		<ModalFooter class="d-lg-flex justify-content-between align-items-center">
			<div>
				<div class="form-check form-switch">
					<input
						name="acept_t"
						id="acept_t"
						class="form-check-input"
						type="checkbox"
						bind:checked={acept_t}
					/>
					{#if !acept_t}
						<label class="form-check-label text-muted fs-6 fw-bold" for="acept_t">Aceptar</label>
					{/if}
				</div>
			</div>
			<div class="d-flex">
				<Button class="btn-sm me-2" color="success" on:click={() => confirmarMatricula()}
					>Continuar</Button
				>
				<Button class="btn-sm" color="danger" on:click={() => closeConfirmarMatricula()}
					>Cerrar</Button
				>
			</div>
		</ModalFooter>
	</Modal>
	<Modal
		isOpen={mOpenRubro}
		toggle={mToggleRubro}
		size={mSizeRubro}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-lg-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={mToggleRubro}>
			<h4>Detalle de rubros generados</h4>
		</ModalHeader>
		<ModalBody>
			<div class="table-responsive scrollbar">
				<table class="table table_primary tabla_responsive  m-0 p-0">
					<thead class="table-light">
						<tr>
							<th class="text-center">Asignatura</th>
							<th class="text-center">Fecha Asignación</th>
							<th class="text-center">Créditos</th>
							<th class="text-center">Valor</th>
							<th class="text-center">Total</th>
						</tr>
					</thead>
					<tbody class="list">
						{#each aMateriaAsignadas as aMateriaAsignada}
							<tr class="">
								<td class="align-middle ">
									{aMateriaAsignada.asignatura} ({aMateriaAsignada.nivel})
								</td>
								<td class="align-middle text-center">
									{aMateriaAsignada.fecha_asignacion}
								</td>
								<td class="align-middle text-center">
									{aMateriaAsignada.creditos}
								</td>
								<td class="align-middle text-center">
									$ {aMateriaAsignada.valor}
								</td>
								<td class="align-middle text-center">
									$ {aMateriaAsignada.total}
								</td>
							</tr>
						{/each}
					</tbody>
					<tfoot>
						<tr>
							<td colspan="4" class="text-end fw-bold">Total de arancel</td>
							<td class="align-middle text-center">$ {valorArancel}</td>
						</tr>
						<tr>
							<td colspan="4" class="text-end fw-bold">Valor de matrícula</td>
							<td class="align-middle text-center">$ {valorMatricula}</td>
						</tr>
						<tr>
							<td colspan="4" class="text-end fw-bold">Total a pagar</td>
							<td class="align-middle text-center fw-bold">$ {valorTotal}</td>
						</tr>
					</tfoot>
				</table>
			</div>
		</ModalBody>
		<ModalFooter>
			<Button class="btn-sm" color="danger" on:click={() => closeRubro()}>Cerrar</Button>
		</ModalFooter>
	</Modal>

	<Modal
		isOpen={mOpenConfirmarDiferido}
		toggle={mToggleConfirmarDiferido}
		size="md"
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}
	>
		<ModalHeader toggle={() => closeConfirmarDiferir()} class="bg-primary text-white">
			<h4 class="text-white">Confirmar diferido</h4>
		</ModalHeader>
		<ModalBody>
			{@html mensajeConfirmarDiferido}
		</ModalBody>
		<ModalFooter>
			<Button color="success" class="rounded-3 btn-sm" on:click={() => confirmarDiferir()}
				>Diferir</Button
			>
			<Button color="warning" class="rounded-3 btn-sm" on:click={() => closeConfirmarDiferir()}
				>No Diferir</Button
			>
		</ModalFooter>
	</Modal>
	{#if mOpenModal}
		<ModalGenerico
			mToggle={mToggleModal}
			mOpen={mOpenModal}
			{modalContent}
			{mClass}
			title={mTitleModal}
			aData={aDataModal}
			size={mSize}
			on:actionRun={actionRun}
		/>
	{/if}
{:else}
	<div
		class="m-0 vh-100 row justify-content-center align-items-center"
		style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 1000; display: flex; flex-direction: column; align-items: center; justify-content: center;"
	>
		<div class="col-auto text-center">
			<Spinner color="dark" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
