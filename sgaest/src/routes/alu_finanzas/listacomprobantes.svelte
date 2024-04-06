<script context="module" lang="ts">
	import type { Load } from '@sveltejs/kit';
    import { variables } from '$lib/utils/constants';

    let eListadoComprobante = [];
    let ePersona = [];
    let listadocuentas = [];
    let fecha_hoy;
    let matricula_id = 0;
	let puede_PagoTarjeta = false;

	export const load: Load = async ({ fetch }) => {


		const ds = browserGet('dataSession');
		if (ds != null || ds != undefined) {
			const dataSession = JSON.parse(ds);
			const connectionToken = dataSession['connectionToken'];
			const [res, errors] = await apiGET(fetch, 'alumno/finanzas', {
                action: 'listacomprobantes'
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
                        eListadoComprobante = res.data['eListadoComprobante'];
                        ePersona = res.data['ePersona'];
                        listadocuentas = res.data['listadocuentas'];
                        fecha_hoy = res.data['fecha_hoy'];
                        matricula_id = res.data['id_matricula'];
						puede_PagoTarjeta = res.data['habilitaPagoTarjeta'];

				}
			}
		}

		return {
			props: {
                eListadoComprobante,
                ePersona,
                listadocuentas,
                fecha_hoy,
                matricula_id,
				puede_PagoTarjeta

			}
		};
	};
</script>

<script lang="ts">
	import { addToast } from '$lib/store/toastStore';
    import { browserGet,apiPOSTFormData, apiPOST, apiGET } from '$lib/utils/requestUtils';

	import { onMount } from 'svelte';
	import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
	import { loading } from '$lib/store/loadingStore';
	import { navigating } from '$app/stores';
	import ModalGenerico from '$components/Alumno/Modal.svelte';
    import { Button, Icon, Modal, ModalBody, ModalFooter, ModalHeader } from 'sveltestrap';
	import { createEventDispatcher, onDestroy } from 'svelte';
	import { dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones } from 'svelte-dnd-action';

    const dispatch = createEventDispatcher();
	import componenteDetalleFinanza from './_detallefinanza.svelte';
	import { converToDecimal } from '$lib/formats/formatDecimal';
	import { addNotification } from '$lib/store/notificationStore';
	import { Spinner, Tooltip } from 'sveltestrap';
	import Swal from 'sweetalert2';
	import { goto } from '$app/navigation';
	import FilePond, { registerPlugin, supported } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
    export let eListadoComprobante;
    export let ePersona;
    export let listadocuentas;
    export let fecha_hoy;
    export let matricula_id;
	export let puede_PagoTarjeta;

	let load = true;
    let eIdInscripcion = '';
	let open = false;
	let itemsBreadCrumb = [{ text: 'Mis Finanzas', active: true, href: '/alu_finanzas' }, { text: 'Listado de Comprobantes', active: true, href: undefined }];
	let backBreadCrumb = { href: '/alu_finanzas', text: 'Atrás' };
	let aDataModal = {};
	let modalTitle = '';
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
    let email, telefono, fecha_pago, valor_pago, observacion, comprobate_tipo, banco_id;
	const toggle = () => (open = !open);


    let mSizeArchivoInscripcion = 'lg';
	let mOpenArchivoInscripcion = false;
	const mToggleArchivoInscripcion = () => (mOpenArchivoInscripcion = !mOpenArchivoInscripcion);



	$: loading.setNavigate(!!$navigating);
	$: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
	let clasificacion = 0;

    let pondDocumento;
	let nameDocumento = 'fileDocumento';

	onMount(async () => {
		registerPlugin(FilePondPluginFileValidateType);
        if (ePersona) {
			telefono = ePersona.telefono;
			email = ePersona.email;
            fecha_pago = fecha_hoy;
            load = false;
		}
		
	});


	const openArchivoInscripcion = () => {
		loading.setLoading(false, 'Cargando, espere por favor...');
		mSizeArchivoInscripcion = 'lg';
		mOpenArchivoInscripcion = true;

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
			}else{				
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


    const limpiarcampos = () => {
        fecha_pago = fecha_hoy;
        valor_pago = 0;
        observacion = '';
        comprobate_tipo = 0;
        banco_id = 0;

	};

   	const closeArchivoInscripcion = () => {
		mOpenArchivoInscripcion = false;
	};



    const handleInit = () => {
		console.log('FilePond has initialised');
	};

	const handleAddFile = (err, fileItem) => {
		console.log(pondDocumento.getFiles());
		console.log('A file has been added', fileItem);
	};

    const loadAjax = async (data, url, method = undefined) =>
		new Promise(async (resolve, reject) => {
			if (method === undefined) {
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
			} else {
				const [res, errors] = await apiGET(fetch, url, data);
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
			}
		});


    const loadInitial = () =>
		new Promise((resolve, reject) => {
			loadAjax({ action: 'listacomprobantes'}, 'alumno/finanzas', 'GET')
				.then((response) => {
					if (response.value.isSuccess) {
						eListadoComprobante = response.value.data['eListadoComprobante'];
						ePersona = response.value.data['ePersona'];

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


    const saveInfoArchivo = async () => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		const $frmInfoArchivo = document.querySelector('#frmInfoArchivo');
		const formData = new FormData($frmInfoArchivo);

		formData.append('action', 'registropago');
        formData.append('id', matricula_id);
        formData.append('email', email);
        formData.append('telefono', telefono);

        if (!banco_id || banco_id === 0) {
			addNotification({
				msg: 'Favor complete el campo de banco',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('banco_id', banco_id);
		}

        if (!valor_pago || valor_pago === 0) {
			addNotification({
				msg: 'Favor complete el campo valor del pago',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('valor_pago', valor_pago);
		}
        if (!fecha_pago) {
			addNotification({
				msg: 'Favor complete el campo fecha del pago',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('fecha_pago', fecha_pago);
		}


        if (!observacion) {
			addNotification({
				msg: 'Favor complete el campo de observación',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('observacion', observacion);
		}

        if (!comprobate_tipo || comprobate_tipo === 0 ) {
			addNotification({
				msg: 'Favor complete el campo de tipo de comprobante',
				type: 'error',
				target: 'newNotificationToast'
			});
			loading.setLoading(false, 'Cargando, espere por favor...');
			return;
		} else {
			formData.append('comprobate_tipo', comprobate_tipo);
		}



		let fileDocumento = pondDocumento.getFiles();
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
		if (pondDocumento && pondDocumento.getFiles().length > 0) {
			eFileDocumento = pondDocumento.getFiles()[0];
		}
		//console.log(eFileDocumento);
		formData.append('fileDocumento', eFileDocumento.file);

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
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
				loading.setLoading(false, 'Cargando, espere por favor...');
				mOpenArchivoInscripcion = false;
				loadInitial()
                limpiarcampos()
			}
		}
		//addNotification({ msg: 'entro', type: 'error', target: 'newNotificationToast' });
	};




</script>

<svelte:head>
	<title>Listado de comprobantes </title>
</svelte:head>

{#if !load}
<BreadCrumb title="Listado de Comprobantes" items={itemsBreadCrumb} back={backBreadCrumb} />
    



                        <div class="row">
                            <div class="col-12">
                                <div class="card mb-4">
                                    <div class="card-header">
<!--                                         <a class="btn btn-info btn-sm" on:click={() => openArchivoInscripcion()} > <i class="bi bi-file-earmark-plus-fill"></i> Agregar pago</a> &nbsp; -->
										{#if puede_PagoTarjeta}
										<a class="btn btn-warning btn-sm" on:click={() => payRubros()} > <i class="bi bi-currency-exchange"></i> Pagar con tarjeta</a><br>
										{/if}
                                    </div>
                                    <div class="card-body">
                                  
                                        <div class="table-responsive">
                                            <table class="table mb-0 text-nowrap table-hover table-bordered align-middle">
                                                <thead class="table-light">
                                                    <tr>
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >FECHA DE REGISTRO</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >DOCUMENTO</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >PERSONA</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >CARRERA</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >CURSO</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >OBSERVACIÓN</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >FECHA DE PAGO</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >BANCO DESTINO</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >TIPO TRANSACIÓN</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >VALOR</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >ESTADO</th
                                                        >
                                                        <th scope="col" class="border-top-0 text-center" style="text-align: center;"
                                                            >COMPROBANTE</th
                                                        >
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {#if eListadoComprobante.length > 0}
                                                        {#each eListadoComprobante as compro}
                                                            <tr>
                                                                <td class="text-wrap fs-6">
                                                                    <b>{ compro.fecha_creacion }</b>
                                                                </td>
                                                                <td class="fs-6" style="text-align: center;">
                                                                    {#if compro.persona.tipopersona == 1}
                                                                        {#if compro.persona.cedula}
                                                                        {compro.persona.cedula} <br>
                                                                        {/if}
                                                                        {#if compro.persona.pasaporte}
                                                                        {compro.persona.pasaporte} <br>
                                                                        {/if}
                                                                    {:else}
                                                                        {compro.persona.ruc}
                                                                    {/if}
                                                                </td>
                                                                <td class="fs-6" style="text-align: left;">
                                                                    <b>{compro.persona.nombre_completo}</b>  <br>
                                                                    <i class="bi bi-telephone-forward"></i> {compro.persona.telefono} <br>
                                                                    <i class="bi bi-envelope"></i> {compro.persona.email}
                                                                </td>
                                                                <td class="fs-6" style="text-align: right;">
                                                                    {compro.carrera}
                                                                </td>
                                                                <td class="fs-6" style="text-align: right;">
                                                                    <b>{compro.curso}</b>
                                                                </td>
                                                                <td class="fs-6" style="text-align: right;">
                                                                    {compro.observacion}

                                                                </td>
                                                                <td class="fs-6" style="text-align: center;">
                                                                    {compro.fechapago}

                                                                </td>
                                                                <td class="fs-6" style="text-align: center;">
                                                                  {compro.cuentadeposito}
                                                                </td>
                                                                <td class="fs-6" style="text-align: center;">
                                                                    {compro.tipocomprobante_nombre}
                                                                </td>
                                                                <td class="fs-6" style="text-align: center; color: green;">
                                                                    <b>${ compro.valor }</b>
                                                                </td>

                                                                <td class="fs-6" style="text-align: center; color: green;">
                                                                    {#if compro.estados == 1}
                                                                    <span class="badge bg-secondary ">{ compro.estados_display }</span>
                                                                    {:else if compro.estados == 2}
                                                                        <span class="badge bg-success ">{ compro.estados_display }</span>

                                                                    {:else if compro.estados == 3}
                                                                        <span class="badge bg-warning ">{ compro.estados_display }</span>

                                                                    {:else if compro.estados == 4}
                                                                        <span class="badge bg-danger ">{ compro.estados_display } </span>

                                                                    {/if}
                                                                </td>
                                                                <td class="fs-6" style="text-align: center;">
                                                                    {#if compro.typefile != '.pdf' }
                                                                            <a title="VER COMPROBANTE" href="{variables.BASE_API}{compro.comprobantes }" target="_blank" class="btn btn-info btn-sm"><i class="bi bi-file-earmark-image"></i></a>
                                                                    {:else}
                                                                             <a title="VER COMPROBANTE" href="{variables.BASE_API}{compro.comprobantes }" target="_blank" class="btn btn-info btn-sm"><i class="bi bi-file-earmark-zip"></i></a>

                                                                    {/if}
                                                                </td>

                                                            </tr>
                                                        {/each}
                                                    {:else}
                                                        <tr>
                                                            <td colspan="8" class="text-center"
                                                                >NO EXISTEN COMPROBANTES DISPONIBLES</td
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



<Modal isOpen={mOpenArchivoInscripcion}
		toggle={mToggleArchivoInscripcion}
		size={mSizeArchivoInscripcion}
		class="modal-dialog modal-dialog-centered modal-dialog-scrollable modal-fullscreen-md-down"
		backdrop="static"
		fade={false}>

		<ModalHeader toggle={mToggleArchivoInscripcion}>
			<h4>Añadir comprobante de pago</h4>
		</ModalHeader>
		<ModalBody>
			<form id="frmInfoArchivo" on:submit|preventDefault={saveInfoArchivo}>
				<div class="card-body">
					<div class="row g-3">
                        <div class="col-md-12">
							<label for="ePersonaSexo" class="form-label fw-bold"
							><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i> Cuenta de banco:</label
						>

						<select class="form-control form-select" id="eCuentaBanco" bind:value={banco_id}>
                            <option value=0>---------</option>
							{#each listadocuentas as cuenta }
								<option value={cuenta[0]}>
									{cuenta[1]} - #:{cuenta[2]} - cta: {cuenta[3]}
								</option>
							{/each}
						</select>
						</div>
                        <div class="col-md-12">
							<label for="ePersonaTelefono" class="form-label fw-bold"> Teléfono  estudiante:
                            </label>
							<input
								type="text"
								class="form-control"
								id="ePersonaTelefono"
								value={telefono}
					
							/>
						</div>
						<div class="col-md-12">
							<label for="ePersonaNombres" class="form-label fw-bold"> Correo electronico estudiante:
                            </label>
							<input
								type="text"
								class="form-control"
								id="ePersonaEmail"
								value={email}
				
							/>
						</div>
						<div class="col-md-6">
							<label for="ePersonaFechaNacimiento" class="form-label fw-bold"
							><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i> Fecha de pago:</label
                            >
                            <input
                                type="date"
                                class="form-control flatpickr-input"
                                id="ePersonaFechaPago"
                                bind:value={fecha_pago}
                            />
						</div>
						<div class="col-md-6">
							<label for="ePersonaApellido2" class="form-label fw-bold"> <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                                Valor:</label>
							<input
                                type="number" step="0.01"
								class="form-control"
								id="ePersonValor"
                                bind:value={valor_pago}

							/>
						</div>
                        <div class="col-md-12">
                            <label for="ePersonaObservacion" class="form-label fw-bold"
                                ><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i> Observación:</label
                            >
                            <textarea
                            rows="3" 
                            cols="100"
                            type="text"
                            class="form-control"
                            id="eObservacion"
                            bind:value={observacion}

                            />
                        </div>
                        <div class="col-md-12">
							<label for="ePersonaSexo" class="form-label fw-bold"
							><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i> Tipo de comprobante:</label
						>

							<select class="form-control form-select" id="ePersonaComprobante" bind:value={comprobate_tipo}>
                                <option value=0>---------</option>

                                {#each [{ value: 1, text: 'DEPOSITO' }, { value: 2, text: 'TRANSFERENCIA' }] as tipo_t}
                                    <option value={tipo_t.value}>
                                        {tipo_t.text}
                                    </option>
                                {/each}
                            </select>
						</div>

						<div class="col-md-12">

							<label for="ePersonaFileDocumento" class="form-label fw-bold"
								><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i> Comprobante:</label
							>
							<!--https://pqina.nl/filepond/docs/api/instance/properties/-->
							<FilePond
								class="pb-0 mb-0"
								id="ePersonaFileDocumento"
								bind:this={pondDocumento}
								{nameDocumento}
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
							<small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small>
						
					</div>
				</div>
				<div class="card-footer text-muted">
					<div class="d-grid gap-2 d-md-flex justify-content-md-end">
						<!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
						<button type="submit" class="btn btn-info">Guardar</button>
						<a color="danger" class="btn btn-danger" on:click={() => closeArchivoInscripcion()}>Cerrar</a>

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
		size="xl"
	/>
{/if}
<style global>
	@import 'filepond/dist/filepond.css';
</style>
