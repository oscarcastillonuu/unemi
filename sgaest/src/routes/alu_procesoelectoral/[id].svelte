<script context="module" lang="ts">
    import type {Load} from '@sveltejs/kit';
    import {session, page, navigating} from '$app/stores';

    export const load: Load = async ({params, fetch}) => {
        const id = params.id;
        const ds = browserGet('dataSession');
        let estados_justificacion = [];
        let filtro = [];
        let listado = [];
        let pk = 0;

        if (ds != null || ds != undefined) {
            const dataSession = JSON.parse(ds);
            const [res, errors] = await apiGET(fetch, 'alumno/procesoelectoral/justificativo', {
                id: id
            });
            if (errors.length > 0) {
                addToast({type: 'error', header: 'Ocurrio un error', body: errors[0].error});
                return {
                    status: 302,
                    redirect: '/'
                };
            } else {
                if (!res.isSuccess) {
                    addToast({type: 'error', header: 'Ocurrio un error', body: res.message});
                    if (!res.module_access) {
                        return {
                            status: 302,
                            redirect: '/'
                        };
                    }
                } else {
                    console.log(res.data);
                    estados_justificacion = res.data['estados_justificacion'];
                    filtro = res.data['filtro'];
                    listado = res.data['listado'];
                    pk = res.data['id'];

                }
            }
        } else {
            return {
                status: 302,
                redirect: '/alu_procesoelectoral'
            };
        }

        return {
            props: {
                estados_justificacion,
                filtro,
                listado,
                pk,
            }
        };
    };
</script>

<script lang="ts">
    import {apiGET, apiPOST, browserGet, browserSet} from '$lib/utils/requestUtils';
    import {variables} from '$lib/utils/constants';
    import {goto} from '$app/navigation';
    import {addToast} from '$lib/store/toastStore';
    import {loading} from '$lib/store/loadingStore';
    import {onMount} from 'svelte';
    import {addNotification} from '$lib/store/notificationStore';
    import {decodeToken} from '$lib/utils/decodetoken';
    import type {UserResponse} from '$lib/interfaces/user.interface';
    import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
    import ModalFormJustificar from "../alu_procesoelectoral/modal/_FormJustificar.svelte";
    import ModalViewObservacion from "../alu_procesoelectoral/modal/_ViewObservacion.svelte";
    import ModalGenerico from '../../components/Alumno/Modal.svelte';
    let aDataModal = {};
	let aplacement = '';
	let modalDetalleOffCanvasContent;
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenOffCanvasGenerico = false;
	let modalTitle = '';

    export let estados_justificacion;
    export let filtro;
    export let listado;
    export let pk;

    let itemsBreadCrumb = [
        {text: 'Justificación deomisiónal sufragío', active: false, href: '/alu_procesoelectoral'},
    ];
    let backBreadCrumb = {href: '/alu_procesoelectoral', text: 'Atrás'};
    $: loading.setNavigate(!!$navigating);
    $: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
    onMount(async () => {
    });

     const nextProccess = (value) => {
		if (value == 1) {
			location.reload();
		}
	};
     const actionRun = (event) => {
		mOpenModalGenerico = false;
		mOpenOffCanvasGenerico = false;
		const detail = event.detail;
		const action = detail.action;
		const value = detail.value;
		if (action == 'nextProccess') {
			loading.setLoading(false, 'Cargando, espere por favor...');
			nextProccess(value);
		}
	};
     const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

     const loadFormJustificar = async (id) => {
        loading.setLoading(true, 'Cargando, espere por favor...');
        const [res, errors] = await apiGET(fetch, 'alumno/procesoelectoral/justificativo', {
            action: 'loadFormJustificar',
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
                aDataModal = res.data;
                modalDetalleContent = ModalFormJustificar;
                mOpenModalGenerico = !mOpenModalGenerico;
                modalTitle = 'JUSTIFICAR FALTA';
            }
        }
    };



     const loadViewObservacion = async (id) => {
        loading.setLoading(true, 'Cargando, espere por favor...');
        const [res, errors] = await apiGET(fetch, 'alumno/procesoelectoral/justificativo', {
            action: 'loadViewObservacion',
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
                aDataModal = res.data;
                modalDetalleContent = ModalViewObservacion;
                mOpenModalGenerico = !mOpenModalGenerico;
                modalTitle = 'JUSTIFICAR FALTA';
            }
        }
    };

</script>

<svelte:head>
    <title>Justificación de omisión al sufragío</title>
</svelte:head>
<BreadCrumb title="Justificación de omisión al sufragío" items={itemsBreadCrumb} back={backBreadCrumb}/>

<div class='row'>
    <div class='col-lg-12'>
        <div class="headtitle ps-0">
            <h6>{ filtro.cab.nombre }</h6>
        </div>
    </div>
</div>
<div class="container-fluid">

    <div class="row">
        <div class="col-12 pb-2">
            {#if filtro['puede_justificar']}
                <a class="btn btn-success" on:click|preventDefault={() => loadFormJustificar(pk)}>
                    <i class="fa fa-plus-circle"></i> Adicionar Justificativo
                </a>
            {/if}

        </div>
    </div>

    <div class="row">
        <div class="col-lg-12 mt-2">
            <div class="table-responsive-xxl">
                <table class='table table_primary table_striped'>
                    <thead>
                    <tr>
                        <th></th>
                        <th class="column-title" style="text-align: center"><span>Fecha Solicitud</span></th>
                        <th class="column-title" style="text-align: center"><span>Documentos</span></th>
                        <th class="column-title" style="text-align: center"><span>Observación</span></th>
                        <th class="column-title" style="text-align: center"><span>Estados</span></th>
                        <th class="column-title" style="text-align: center">Acciones</th>
                    </tr>
                    </thead>
                    <tbody>
                    {#each listado as p }
                        <tr>
                            <td></td>
                            <td style="text-align: center;">{p.fecha_creacion}</td>
                            <td style="text-align: center">
                                {#if p.certificado_medico}
                                    <b>Certificado médico de centro de salud publica o IESS:</b>
                                    {#if !p.tf_certificado_medico == '.pdf' }
                                        <a data-fancybox="image" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Impedimento físico o enfermedad"
                                           href="{variables.BASE_API}{ p.certificado_medico }"><img
                                                style="margin-top: 2px; width: 25px"
                                                src="{variables.BASE_API_STATIC}/images/image.png"/></a>
                                    {:else}
                                        <a data-fancybox="iframe" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Impedimento físico o enfermedad"
                                           href="{variables.BASE_API}{ p.certificado_medico }"><img style="margin-top: 2px;"
                                                                                       src="{variables.BASE_API_STATIC}/images/pdf.png"/>
                                        </a>
                                    {/if}
                                {/if}
                                {#if p.certificado_upc}
                                    <b>Certificado de UPC de haber sido detenido:</b>
                                    {#if !p.tf_certificado_upc == '.pdf' }
                                        <a data-fancybox="image" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           title="Fué detenido el día de las elecciones"
                                           href="{variables.BASE_API}{p.certificado_upc }">
                                            <img style="margin-top: 2px; width: 25px"
                                                 src="{variables.BASE_API_STATIC}/images/image.png"/></a>
                                    {:else }
                                        <a data-fancybox="iframe" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Fué detenido el día de las elecciones"
                                           href="{variables.BASE_API}{ p.certificado_upc }">
                                            <img style="margin-top: 2px;"
                                                 src="{variables.BASE_API_STATIC}/images/pdf.png"/>
                                        </a>
                                    {/if}
                                {/if}
                                {#if p.certificado_defuncion }
                                    <b> Certificado de defunción:</b>
                                    {#if !p.tf_certificado_defuncion == '.pdf'}
                                        <a data-fancybox="image" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Fallecio un familiar hasta de 4to grado de consanguinidad"
                                           href="{variables.BASE_API}{ p.certificado_defuncion }"><img
                                                style="margin-top: 2px; width: 25px"
                                                src="{variables.BASE_API_STATIC}/images/image.png"/></a>
                                    {:else}
                                        <a data-fancybox="iframe" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Fallecio un familiar hasta de 4to grado de consanguinidad"
                                           href="{variables.BASE_API}{ p.certificado_defuncion }"><img style="margin-top: 2px;"
                                                                                          src="{variables.BASE_API_STATIC}/images/pdf.png"/></a>
                                    {/if}
                                {/if}
                                {#if p.certificado_licencia}
                                    <b> Cuenta con licencia y no pudo presentarse al sufragio:</b>
                                    {#if !p.tf_certificado_licencia == '.pdf'}
                                        <a data-fancybox="image" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Cuenta con licencia y no pudo presentarse al sufragio"
                                           href="{variables.BASE_API}{ p.certificado_licencia }"><img style="margin-top: 2px; width: 25px" src="{variables.BASE_API_STATIC}/images/image.png"/></a>
                                    {:else}
                                        <a data-fancybox="iframe" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Cuenta con licencia y no pudo presentarse al sufragio"
                                           href="{variables.BASE_API}{ p.certificado_licencia }"><img style="margin-top: 2px;" src="{variables.BASE_API_STATIC}/images/pdf.png"/></a>
                                    {/if}
                                {/if}
                                {#if p.certificado_alterno}
                                    <b> Cuenta con un justificativo distinto a las causales anteriores:</b>
                                    {#if !p.tf_certificado_alterno == '.pdf'}
                                        <a data-fancybox="image" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Cuenta con un justificativo distinto a las causales anteriores"
                                           href="{variables.BASE_API}{ p.certificado_alterno }"><img style="margin-top: 2px; width: 25px" src="{variables.BASE_API_STATIC}/images/image.png"/></a>
                                    {:else}
                                        <a data-fancybox="iframe" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           title="Cuenta con un justificativo distinto a las causales anteriores"
                                           href="{variables.BASE_API}{ p.certificado_alterno }"><img style="margin-top: 2px;"  src="{variables.BASE_API_STATIC}/images/pdf.png"/></a>
                                    {/if}
                                {/if}
                                {#if p.documento_validador}
                                    <b> Copia de cédula o copia de papeleta de votaciòn o certificado emitido por UPC de vivienda:</b>
                                    {#if !p.tf_documento_validador == '.pdf'}
                                        <a data-fancybox="image" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Subir, Copia de cédula o copia de papeleta de votaciòn o certificado emitido por UPC de vivienda"
                                           href="{variables.BASE_API}{ p.documento_validador }"><img style="margin-top: 2px; width: 25px" src="{variables.BASE_API_STATIC}/images/image.png"/></a>
                                    {:else}
                                        <a data-fancybox="iframe" class="btn tu" data-width="2048" data-height="1365" target="_blank"
                                           data-caption="Subir, Copia de cédula o copia de papeleta de votaciòn o certificado emitido por UPC de vivienda"
                                           href="{variables.BASE_API}{ p.documento_validador}"><img style="margin-top: 2px;"  src="{variables.BASE_API_STATIC}/images/pdf.png"/></a>
                                    {/if}
                                {/if}
                            </td>
                            <td style="text-align: center">
                                {p.observacion}
                            </td>
                            <td style="text-align: center">
                                {#if p.estados_justificacion == 0 }
                                    <span
                                        className="text-info">{p.estado_display}</span>
                                {/if}

                                {#if p.estados_justificacion == 1 }<span
                                        className="text-warning">{p.estado_display}</span>{/if}

                                {#if p.estados_justificacion == 2 } <span
                                        className="text-success">{p.estado_display}</span>{/if}

                                {#if p.estados_justificacion == 3}<span
                                        className="text-danger">{p.estado_display}</span>{/if}

                                {#if p.get_lastobser}<br>
                                    <b>Fecha Hora:</b> {p.get_lastobser.fecha_creacion}
                                    {p.get_lastobser.fecha_creacion}
                                {/if}


                            </td>
                            <td style="text-align: center">
                                <a on:click|preventDefault={() => loadViewObservacion(pk)}   class="btn btn-info btn-mini tb" title="Ver Observaciones" href="javascript:void(0);"> <i class='fe fe-eye'></i></a>
                                <!--{#if p.estados_justificacion == 2 }-->
                                <!--    <a href="Javascript:void(0);"-->
                                <!--       class="btn btn-warning btn-mini tl" target="_blank"-->
                                <!--       title="Generar Certificado"></a>-->
                                <!--{/if}-->
                            </td>
                        </tr>
                    {:else}
                        <tr>
                            <td colspan="7">NO EXISTEN REGISTROS</td>
                        </tr>
                    {/each}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

</div>



<style>
    /* 	CSS variables can be used to control theming.
            https://github.com/rob-balfre/svelte-select/blob/master/docs/theming_variables.md
    */


    .table_striped tbody tr:nth-child(even), .table_striped tbody tr:nth-child(even) {
        background-color: #e7eef5;
    }

    .table_striped tbody tr:nth-child(odd), .table_striped tbody tr:nth-child(odd) {
        background-color: #f2f6fb;
    }

    .table_striped thead th, .table_striped thead td, .table_striped tbody th, .table_striped tbody td {
        border-right: 1px solid white;
    }

    .table_striped thead th:nth-child(1), .table_striped thead th:nth-child(2), .table_striped thead td:nth-child(1), .table_striped thead td:nth-child(2), .table_striped tbody td:nth-child(1), .table_striped tbody td:nth-child(2), .table_striped tbody th:nth-child(1), .table_striped tbody th:nth-child(2) {
        border-right: none;
    }

    .table_striped thead th:nth-child(2), .table_striped thead td:nth-child(2) {
        text-align: left !important;
        padding-left: 15px
    }

    .table_striped a.btn {
        padding-bottom: 0.5rem !important;
        padding-top: 0.5rem !important;
    }

    .table_striped a.btn .fa {
        font-size: 9px;
        margin-right: 3px
    }

    .table_striped thead th {
        text-align: center;
        color: #1e121e;
        font-size: 13px;
        vertical-align: middle;
        text-transform: uppercase;
    }


    .table_primary thead th {
        background-color: #abcae6;
    }

    .table_primary thead th:first-child, .table_primary thead td:first-child {
        width: 20px;
        background-color: #1c3247
    }

    .table_primary tbody th, .table_primary tbody td {
        font-size: 13px;
        vertical-align: middle !important
    }

    .table_warning thead th {
        background-color: #f9ebd6;
    }

    .table_warning thead th:first-child, .table_warning thead td:first-child {
        width: 20px;
        background-color: #fe9900
    }

    .table_warning tbody th, .table_warning tbody td {
        font-size: 13px;
        vertical-align: middle !important
    }

    .table_danger thead th {
        background-color: #FADBD8;
    }

    .table_danger thead th:first-child, .table_danger thead td:first-child {
        width: 20px;
        background-color: #E74C3C
    }

    .table_danger tbody th, .table_danger tbody td {
        font-size: 13px;
        vertical-align: middle !important
    }

    .propiedades {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    form {
        /*max-width: 400px;*/
        background: #f4f4f4;
        padding: 0;
        border-radius: 4px;
    }

    label {
        margin: 0 0 10px;
    }

    .themed {
        --border: 3px solid blue;
        --borderRadius: 10px;
        --placeholderColor: blue;
    }
</style>

{#if mOpenModalGenerico}
    <ModalGenerico
            mToggle={mToggleModalGenerico}
            mOpen={mOpenModalGenerico}
            modalContent={modalDetalleContent}
            title={modalTitle}
            aData={aDataModal}
            size="xl"
            on:actionRun={actionRun}
    />
{/if}


