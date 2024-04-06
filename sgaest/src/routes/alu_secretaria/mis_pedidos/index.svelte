<script context="module" lang="ts">
	import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import type { Load } from '@sveltejs/kit';
	import { addToast } from '$lib/store/toastStore';

	let puede_PagoTarjeta = false;

	export const load: Load = async ({ fetch }) => {
		const ds = browserGet('dataSession');
		let ePersona = {};
		//console.log(ds);
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			ePersona = dataSession['persona'];
			loading.setLoading(true, 'Cargando, espere por favor...');
			const [res, errors] = await apiGET(fetch, 'alumno/secretary/solicitud', {
				action: 'validateInitLoad'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
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
					puede_PagoTarjeta = res.data['habilitaPagoTarjeta'];
				}
			}
		}

		return {
			props: {
				ePersona,
				puede_PagoTarjeta
			}
		};
	};
</script>

<script lang="ts">
	import Swal from 'sweetalert2';
	import { onMount } from 'svelte';
	import { variables } from '$lib/utils/constants';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';
	import { loading } from '$lib/store/loadingStore';
	import { goto } from '$app/navigation';
	import { navigating } from '$app/stores';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import Grid from 'gridjs-svelte';
	import { logOutUser } from '$lib/utils/requestUtils';
	import { h, html } from 'gridjs';

	import ComponenteHistorial from './_historialsolicitud.svelte';
	import ModalGenerico from '$components/Alumno/Modal.svelte';

	export let ePersona;
	export let puede_PagoTarjeta;
	let grid;

	/* variables modal */
	let aDataModal = {};
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let modalTitle = '';
	let modalSize = 'xl';

	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

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

	const actionDelete = async (eSolicitud) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, va a eliminar <b>${eSolicitud.descripcion}</b></br><b>¿Está ${
				ePersona.sexo_id === 1 ? 'segura' : 'seguro'
			} de eliminar?</b>`,
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
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'delete',
							id: eSolicitud.id
						},
						'alumno/secretary/solicitud'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								addToast({ type: 'success', header: 'Exitoso!', body: response.value.message });
								grid.forceRender();
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
	};

	const actionGenerateRubro = async (eSolicitud) => {
		const mensaje = {
			title: `NOTIFICACIÓN`,
			html: `${ePersona.sexo_id === 1 ? 'Estimada' : 'Estimado'} ${
				ePersona.nombre_completo
			}, está por generar el rubro por concepto de habilitación del proceso de 
			titulación extraordinaria por un valor de <span class="badge bg-warning text-dark">$${eSolicitud.costo2modulos}</span> equivalente 
			a dos módulos del programa de <b>${eSolicitud.maestria}</b></br><b>¿Está ${
				ePersona.sexo_id === 1 ? 'segura' : 'seguro'
			} de generar su valor a pagar?</b> <br> Recuerde que este valor no es reembolsable.`,
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
					loading.setLoading(true, 'Cargando, espere por favor...');
					loadAjax(
						{
							action: 'generarrubro2modulos',
							id: eSolicitud.id
						},
						'alumno/secretary/solicitud'
					)
						.then((response) => {
							loading.setLoading(false, 'Cargando, espere por favor...');
							if (response.value.isSuccess) {
								addToast({ type: 'success', header: 'Exitoso!', body: response.value.message });
								grid.forceRender();
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
	};

	const actionViewDetail = async (id) => {
		/* console.log(eSolicitud);
		console.log(grid);
		grid.forceRender(); */
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/secretary/solicitud', {
			action: 'historial',
			id: id
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
			console.log(errors);
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				console.log(res.data);
				aDataModal = res.data;
				modalDetalleContent = ComponenteHistorial;
				mOpenModalGenerico = !mOpenModalGenerico;
				modalTitle = 'Historial de Solicitud';
			}
		}

		/* aDataModal = { eSolicitud: eSolicitud };
		modalDetalleContent = ComponenteHistorial;
		mOpenModalGenerico = !mOpenModalGenerico;
		modalTitle = 'Historial de Solicitud';
		//modalSize = 'xs'; */
	};
/*
	const openSolicitudFisicaEditar = async (id) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/secretary/solicitud', {
			action: 'editarsolicitudfisica',
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
				a=0
			}
		}
		mSizeComprobante = 'lg';
		mOpenModalGenerico = true;
		titleComprobante = 'Registro de comprobantes';
	};
*/
	const actionViewDownloand = async (archivo) => {
		//console.log(archivo);
		window.open(archivo, '_blank');
	};

	const generarDescarga = async (solicitud) => {
		loading.setLoading(true, 'Cargando, espere por favor...');
		const [res, errors] = await apiPOST(fetch, 'alumno/secretary/solicitud', {
			action: 'descargacertificado',
			id: solicitud
		});
		loading.setLoading(false, 'Cargando, espere por favor...');
		if (errors.length > 0) {
			addNotification({
				msg: errors[0].error,
				type: 'error'
			});
			console.log(errors);
		} else {
			if (!res.isSuccess) {
				addNotification({
					msg: res.message,
					type: 'error'
				});
			} else {
				//console.log(res.data);
				addToast({ type: 'success', header: 'Exitoso!', body: res.data.mensaje });
				location.reload();
			}
		}
	};

	const columns = [
		{
			name: 'Código',
			sort: false,
			width: '10%'
		},
		{
			name: 'Fecha/Hora',
			sort: false,
			width: '10%'
			/*formatter: (cell) => {
				return `${cell.fecha} ${cell.hora}`
			}*/
		},
		{
			name: 'Solicitud/Servicio',
			sort: false,
			width: '35%'
		},
		/* {
			name: 'Valor a Pagar',
			sort: false,
			width: '14%'
		}, */
		{
			name: 'Fecha Limite',
			sort: false,
			width: '10%'
		},
		{
			name: 'Estado',
			sort: false,
			width: '15%',
			style: { 'text-align': 'center' }
		},
		{
			name: 'Archivo',
			sort: false,
			width: '10%',
			style: { 'text-align': 'center' },
			formatter: (cell, row) => {
				const btns = [];
				const eSolicitud = row.cells[5].data;
				console.log('eSolicitud:', eSolicitud);
				if (eSolicitud.valor_unitario > 0 && eSolicitud.servicio.categoria.pk !== 6) {
					if ((eSolicitud.servicio.proceso == 8 && eSolicitud.estado == 1 && eSolicitud.certificado.pk == 51) || (eSolicitud.servicio.proceso == 8 && eSolicitud.estado != 2 && [55].includes(eSolicitud.certificado.pk))) {
						let ruta = variables.BASE_API + eSolicitud.archivo_solicitud_fisica;
						btns[0] = h(
							'button',
							{
								className: 'btn btn-link btn-sm p-0 m-0',
								onClick: async () => await actionViewDownloand(ruta)
							},
							html(
								'<i class="bi bi-envelope-check-fill" style="font-size: 1.7rem; color: #198754;"></i>'
							)
						);
					} else {
						if (eSolicitud.estado === 2) {
							if (eSolicitud.archivo_respuesta) {
								btns[0] = h(
									'button',
									{
										className: 'btn btn-link btn-sm p-0 m-0',
										onClick: async () => await actionViewDownloand(eSolicitud.archivo_respuesta)
									},
									html('<i class="bi bi-download" style="font-size: 1.7rem; color: #198754;"></i>')
								);
							} else {
								btns[0] = h(
									'button',
									{
										className: 'btn btn-link btn-sm p-0 m-0',
										onClick: async () => await generarDescarga(eSolicitud.id)
									},
									html(
										'<i class="bi bi-bootstrap-reboot" data-toggle="tooltip" title="Descargar archivo" style="font-size: 1.7rem; color: #198754;"></i>'
									)
								);
							}
						} 
					}
				} else if (eSolicitud.estado == 16) {
							btns[0] = h(
									'button',
									{
										className: 'btn btn-link btn-sm p-0 m-0',
										onClick: async () => await actionViewDownloand(eSolicitud.archivo_solicitud)
									},
									html('<i class="bi bi-download" style="font-size: 1.7rem; color: #198754;"></i>')
								);
						}
				return btns;
			}
		},
		{
			name: '',
			sort: false,
			width: '10%',
			style: { 'text-align': 'center' },
			formatter: (cell, row) => {
				const btns = [];
				const eSolicitud = row.cells[5].data;
				let contador = 0;
				if (eSolicitud.puede_eliminar) {
					btns[contador] = h(
						'button',
						{
							className: 'btn btn-link btn-sm p-0 m-0',
							onClick: async () =>
								//alert(`Editing "${eSolicitud['puede_eliminar']}" "${eSolicitud['id']}"`)
								await actionDelete(eSolicitud)
						},
						html('<i class="bi bi-trash-fill" style="font-size: 1.7rem; color: Crimson;"></i>')
					);
					contador += 1;
				}
				if (eSolicitud.estado === 12) {
					btns[contador] = h(
						'button',
						{
							className: 'btn btn-link btn-sm p-0 m-0',
							onClick: async () =>
								//alert(`Editing "${eSolicitud['puede_eliminar']}" "${eSolicitud['id']}"`)
								await actionGenerateRubro(eSolicitud)
						},
						html('<i class="bi bi-cash-coin" title="Generar rubro" style="font-size: 1.7rem; color: #198754;"></i>')
					);
					contador += 1;
				}
				btns[contador] = h(
					'button',
					{
						className: 'btn btn-link btn-sm p-0 m-0',
						onClick: async () =>
							//alert(`Editing "${eSolicitud['puede_eliminar']}" "${eSolicitud['id']}"`)
							//await actionViewDetail(JSON.stringify(eSolicitud))
							//await actionViewDetail(eSolicitud.id)
							await actionViewDetail(eSolicitud.id)
					},
					html(
						'<i class="bi bi-view-list" data-toggle="tooltip" title="Ver historial" style="font-size: 1.7rem; color: #1a3bd6;"></i>'
					)
				);
				
/*				contador += 1;
				if (eSolicitud.servicio.proceso == 8 && (eSolicitud.estado == 1 || eSolicitud.estado == 2)) {
					btns[contador] = h(
						'button',
						{
							className: 'btn btn-link btn-sm p-0 m-0',
							onClick: async () =>
								//alert(`Editing "${eSolicitud['puede_eliminar']}" "${eSolicitud['id']}"`)
								//await actionViewDetail(JSON.stringify(eSolicitud))
								//await actionViewDetail(eSolicitud.id)
								await actionViewDetail(eSolicitud.id)
						},
						html(
							'<i class="bi bi-pencil-square" data-toggle="tooltip" title="Ver historial" style="font-size: 1.7rem; color: #1a3bd6;"></i>'
						)
					);
				}*/
				return btns;
			}
		}
		/*{
			name: 'Date',
			formatter: (cell) => {
				return new Date(cell).toLocaleString('en-US', {
					month: 'short',
					year: 'numeric'
				});
			}
		}*/
	];
	let load = true;
	let itemsBreadCrumb = [
		{ text: 'Secretaría', active: false, href: '/alu_secretaria' },
		{ text: `Mis pedidos`, active: true, href: undefined }
	];
	let backBreadCrumb = { href: '/alu_secretaria', text: 'Atrás' };

	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

	onMount(async () => {});

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
</script>

<svelte:head>
	<title>Secretaría - Mis pedidos</title>
</svelte:head>
<!-- {#if !load} -->
<BreadCrumb title="Mis pedidos de secretaría" items={itemsBreadCrumb} back={backBreadCrumb} />
<div class="card-header">
	{#if puede_PagoTarjeta}
		<a class="btn btn-warning btn-sm" on:click={() => payRubros()}>
			<i class="bi bi-currency-exchange" /> Pagar con tarjeta o transferencia</a
		><br />
	{/if}
</div>
<div class="table-responsive-md">
	<Grid
		bind:instance={grid}
		{columns}
		autoWidth={true}
		resizable={true}
		fixedHeader={true}
		className={{
			td: '',
			table: 'table table-strip table-hover'
		}}
		sort
		pagination={{
			enabled: true,
			limit: 25,
			server: {
				url: (prev, page, limit) =>
					`${prev.includes('search') ? `${prev}&limit` : `${prev}?limit`}=${limit}&offset=${
						page * limit
					}`
			}
		}}
		search={{
			server: {
				url: (prev, keyword) => `${prev}?search=${keyword}`
			}
		}}
		server={{
			url: `${variables.BASE_API_URI}/alumno/secretary/solicitud`,
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer ${browserGet('accessToken')}`
			},
			then: (response) =>
				response.data.eSolicitudes.map((eSolicitud) => {
					return [
						html(`<div class="text-break">${eSolicitud.codigo}</div>`),
						html(`<div class="text-break">${eSolicitud.fecha} ${eSolicitud.hora}</div>`),
						html(`<div class="text-break" style="text-align:left">${eSolicitud.descripcion}</div>`),
						/* html(`<div class="text-break">$ ${eSolicitud.total}</div>`), */
						html(`<div class="text-break"> ${eSolicitud.fecha_limite_pago}</div>`),
						html(
							`<div class="text-break"><span class="badge rounded-pill text-dark" style="${eSolicitud.color_estado_display}">${eSolicitud.estado_display} </span></div>`
						),
						eSolicitud,
						eSolicitud
					];
				}),
			total: (response) => response.data.count
		}}
		language={{
			search: {
				placeholder: '🔍 Buscar...'
			},
			pagination: {
				//previous: '⬅️',
				previous: () => html('<i class="bi bi-chevron-left"></i>'),
				//next: '➡️',
				next: () => html('<i class="bi bi-chevron-right"></i>'),
				showing: '😃 Mostrando registros del',
				of: 'de un total de',
				to: 'al',
				results: 'registros',
				//results: () => 'Registros',
				navigate: function (e, r) {
					return `Página ${e} de ${r}`;
				},
				page: function (e) {
					return 'Página ' + e;
				}
			},
			loading: 'Cargando...',
			noRecordsFound: 'No se encontraron registros',
			error: 'Se produjo un error al recuperar datos',
			sort: {
				sortAsc: 'Ordenar la columna en orden ascendente',
				sortDesc: 'Ordenar la columna en orden descendente'
			}
		}}
	/>
</div>

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
	/*@import 'https://cdn.jsdelivr.net/npm/gridjs/dist/theme/mermaid.min.css';*/
	@import '/static/assets/css/mermaid.min.css';
	/*.table {
		table-layout: fixed;
	}*/
	table.gridjs-table {
		table-layout: fixed;
	}
	/* On screens that are 992px or less, set the background color to blue */
	@media screen and (max-width: 992px) {
		table.gridjs-table {
			table-layout: auto;
		}
	}

	/* On screens that are 600px or less, set the background color to olive */
	@media screen and (max-width: 600px) {
		table.gridjs-table {
			table-layout: auto;
		}
	}
	.gridjs-th {
		padding: 10px 15px !important;
		text-align: center;
	}
	.gridjs-td {
		padding: 5px 10px !important;
		text-align: center;
		vertical-align: middle;
	}
</style>
