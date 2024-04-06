<script context="module" lang="ts">
    import {browserGet, apiPOST, apiGET} from '$lib/utils/requestUtils';
    import type {Load} from '@sveltejs/kit';
    import {addToast} from '$lib/store/toastStore';
    import {Spinner, Tooltip} from 'sveltestrap';
    import {
        Button,
        Icon,
        Modal,
        ModalBody,
        ModalFooter,
        ModalHeader,
        Alert,
        Badge,
        ButtonDropdown,
        DropdownItem,
        DropdownMenu,
        DropdownToggle,
        Form,
        FormGroup,
        Input,
        Label,
        FormText,
        Offcanvas
    } from 'sveltestrap';

    export const load: ({fetch}: { fetch: any }) => Promise<{ redirect: string; status: number } | string | { redirect: string; status: number } | { redirect: string; status: number } | { props: { procesoactivo: any[]; listvigente: any[]; listpasados: any[]; soliprocesoactivos: any[] } }> = async ({fetch}) => {
        let procesoactivo = [];
        let soliprocesoactivos = [];
        let listvigente = [];
        let listpasados = [];

        const ds = browserGet('dataSession');
        //console.log(ds);
        if (ds != null || ds != undefined) {
            const dataSession = JSON.parse(ds);
            const connectionToken = dataSession['connectionToken'];
            loading.setLoading(true, 'Cargando, espere por favor...');
            const [res, errors] = await apiGET(fetch, 'alumno/procesoelectoral', {});
            loading.setLoading(false, 'Cargando, espere por favor...');
            if (errors.length > 0) {
                addToast({
                    type: 'error',
                    header: 'Ocurrio un error',
                    body: errors[0].error
                });
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
                                addToast({type: 'error', header: 'Ocurrio un error', body: res.message});
                                return {
                                    status: 302,
                                    redirect: `${res.redirect}`
                                };
                            }
                        } else {
                            addToast({type: 'error', header: 'Ocurrio un error', body: res.message});
                            return {
                                status: 302,
                                redirect: '/'
                            };
                        }
                    }
                } else {
                    console.log(res.data);
                    procesoactivo = res.data['procesoactivo'];
                    soliprocesoactivos = res.data['soliprocesoactivos'];
                    listvigente = res.data['listvigente'];
                    listpasados = res.data['listpasados'];

                }
            }
        }
        return {
            props: {
                procesoactivo,
                soliprocesoactivos,
                listvigente,
                listpasados

            }
        };
    };
</script>

<script lang="ts">
    import {onMount} from 'svelte';
    import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
    import {loading} from '$lib/store/loadingStore';
    import {navigating} from '$app/stores';
    import ModalGenerico from '$components/Alumno/Modal.svelte';
    import OffCanvasGenerico from '$components/Alumno/OffCanvasModal.svelte';
    import {addNotification} from '$lib/store/notificationStore';
    import FormModalSolicitarInfo from "../alu_procesoelectoral/modal/_FormSolicitarInformacion.svelte";

    let aDataModal = {};
    let aplacement = '';
    let modalDetalleOffCanvasContent;
    let modalDetalleContent;
    let mOpenModalGenerico = false;
    let mOpenOffCanvasGenerico = false;
    let modalTitle = '';
    export let procesoactivo;
    export let soliprocesoactivos;
    export let listvigente;
    export let listpasados;

    const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);
    const mToggleOffCanvasGenerico = () => (mOpenOffCanvasGenerico = !mOpenOffCanvasGenerico);
    let itemsBreadCrumb = [
        {
            text: 'Proceso electoral',
            active: true,
            href: undefined
        }
    ];
    let backBreadCrumb = {
        href: '/',
        text: 'Atrás'
    };
    $: loading.setNavigate(!!$navigating);
    $: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');

    onMount(async () => {

    });

    const loadAjax = async (data, url, method = undefined) =>
        new Promise(async (resolve, reject) => {
            if (method === undefined) {
                const [res, errors] = await apiPOST(fetch, url, data);
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
            loading.setLoading(true, 'Cargando, espere por favor...');
            loadAjax({}, 'alumno/procesoelectoral', 'GET')
                .then((response) => {
                    if (response.value.isSuccess) {
                        procesoactivo = response.value.data['procesoactivo'];
                        soliprocesoactivos = response.value.data['soliprocesoactivos'];
                        listvigente = response.value.data['listvigente'];
                        listpasados = response.value.data['listpasados'];

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
            loading.setLoading(false, 'Cargando, espere por favor...');
        });

    const nextProccess = (value) => {
        if (value == 1) {
            loadInitial();
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

    const loadFormSolicitarInformacion = async (pk) => {
        loading.setLoading(true, 'Cargando, espere por favor...');
        const [res, errors] = await apiGET(fetch, 'alumno/procesoelectoral', {
            action: 'loadFormSolicitarInformacion',
            id: pk,
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
                modalDetalleContent = FormModalSolicitarInfo;
                mOpenModalGenerico = !mOpenModalGenerico;
                modalTitle = 'SOLICITAR INFORMACIÓN';
            }
        }
    };


</script>

<!-- mis componentes -->

<svelte:head>
    <title>Proceso electoral</title>
</svelte:head>
<BreadCrumb title="Proceso electoral" items={itemsBreadCrumb} back={backBreadCrumb}/>

<div class="container-fluid">
    {#if procesoactivo.length > 0 || soliprocesoactivos.length > 0 || listvigente.length > 0 || listpasados.length > 0 || procesoactivo.length != '' || soliprocesoactivos.length != '' || listvigente.length != '' || listpasados.length != '' }
        <div class="row">
            <div class="col-lg-12 mt-5">
                <div class="table-responsive">
                    {#if !listvigente.length > 0 || !listvigente != ''}
                        {#if procesoactivo.length > 0 || procesoactivo != ''}

                             <h3 style="font-size: 19px;"><i class="fa fa-warning text-danger fs-3"></i> ¿Deseas generar un
                            reclamo de conformación del padrón electoral? <a class="btn btn-orange fs-5" on:click={() =>loadFormSolicitarInformacion(procesoactivo.pk)}
                                                                             href="javascript:void(0);"><i
                                    class="fe fe-plus-circle"></i> Llenar formulario</a></h3>
                            {#if soliprocesoactivos.length > 0 || soliprocesoactivos != ''}<br>
                                <table class='table table_danger table_striped'>
                                    <thead>
                                    <tr>
                                        <th></th>
                                        <th class="column-title text-left" style="width: 30%">Solicitud</th>
                                        <th class="column-title text-left" style="width: 40%">Observación</th>
                                        <th class="column-title text-center" style="width: 30%">Respuesta</th>
                                    </tr>
                                    </thead>
                                    <tbody>
                                    {#each soliprocesoactivos as p }
                                        <tr>
                                            <td></td>
                                            <td class="text-left">
                                                {p.cab.nombre}
                                            </td>
                                            <td class="text-left p-lg-5">
                                                <b>Categoría:</b> {p.tipo.display} <br>
                                                <b>Obs.</b> { p.observacion } <br>
                                                <b>F. Creación:</b> { p.fecha_creacion} <br>
                                                <b>Estado:</b>
                                                {#if p.estados == 0 }
                                                    <span class="text-primary">{ p.estados_display }</span> {/if}
                                                {#if p.estados == 1 }
                                                    <span class="text-success">{ p.estados_display }</span> {/if}
                                                {#if p.estados == 2 }
                                                    <span class="text-danger">{ p.estados_display }</span>
                                                {/if}
                                            </td>
                                            <td class="text-left p-lg-5">
                                                {#if p.estados == 0 }
                                                    <center>
                                                        <span class="text-danger"><i class="fe fe-history"></i> Pendiente</span>
                                                    </center>
                                                {:else}
                                                    <b>F. Validación:</b> {p.fechavalidacion}<br>
                                                    <b>Resp.</b> {p.respuesta }

                                                {/if}
                                            </td>
                                        </tr>
                                    {:else}
                                        <tr>
                                            <td colspan="10" style="text-align: center">NO EXISTEN NINGUN
                                                JUSTIFICATIVO
                                            </td>
                                        </tr>
                                    {/each}
                                    </tbody>
                                </table>
                            {/if}
                        {/if}
                    {:else }

                        <table class='table table_primary table_striped'>
                            <thead>
                            <tr>
                                <th></th>
                                <th class="column-title text-left" style="width: 100%">Procesos Activos</th>
                                <th class="column-title text-center" style="width: 30%"></th>
                            </tr>
                            </thead>
                            <tbody>
                            {#each listvigente as p }
                                <tr>
                                    <td></td>
                                    <td class="text-left">
                                        { p.cab.nombre } - <b class="text-primary">{ p.tipo }</b><br>
                                        <i class="fe fe-calendar"></i> Fecha de elección: {p.cab.fecha}<br>
                                        {#if p.info_mesa}
                                            <b class="text-error">
                                                <i class="fa fa-vote-yea"></i> Miembro de Junta Receptora del Voto:
                                                <br>

                                            </b>
                                        {/if}

                                    </td>

                                    <td class="text-center">
                                        {#if p.cab.puede_justificar }
                                            <a class="btn btn-primary" href="/alu_procesoelectoral/{p.pk}">justificar</a>
                                        {/if}

                                    </td>
                                </tr>
                            {:else}
                                <tr>
                                    <td colspan="10" style="text-align: center">Ningún dato disponible en esta tabla
                                    </td>
                                </tr>
                            {/each}

                            </tbody>
                        </table>
                    {/if}

                </div>
            </div>

            <div class="col-lg-12 mt-5">
                <div class="table-responsive">
                    <!--                    <table class='table table_warning table_striped'>-->
                    <!--                        <thead>-->
                    <!--                        <tr>-->
                    <!--                            <th></th>-->
                    <!--                            <th class="column-title text-left" style="width: 70%">Procesos Pasados</th>-->
                    <!--                            <th class="column-title text-center" style="width: 20%">Lugar de votación</th>-->
                    <!--                            <th class="column-title text-center" style="width: 30%"></th>-->
                    <!--                        </tr>-->
                    <!--                        </thead>-->
                    <!--                        <tbody>-->

                    <!--                        {#each listpasados as p }-->
                    <!--                            <tr>-->
                    <!--                                <td></td>-->
                    <!--                                <td class="text-left">-->
                    <!--                                    { p.cab.nombre } - <b class="text-primary">{ p.tipo }</b><br>-->
                    <!--                                    <i class="fe fe-calendar"></i> Fecha de elección: {p.cab.fecha}<br>-->
                    <!--                                    {#if p.info_mesa}-->
                    <!--                                        <b class="text-error">-->
                    <!--                                            <i class="fa fa-vote-yea"></i> Miembro de Junta Receptora del Voto:-->
                    <!--                                            <br>-->


                    <!--                                        </b>-->
                    <!--                                    {/if}-->

                    <!--                                </td>-->
                    <!--                                <td class="text-center">-->
                    <!--                                    {#if p.lugar}{ p.lugar }{/if}-->
                    <!--                                </td>-->
                    <!--                                <td class="text-center">-->
                    <!--                                    <a class="btn btn-warning"  href="/alu_procesoelectoral/{p.pk}">Justificativos</a>-->
                    <!--                                </td>-->
                    <!--                            </tr>-->
                    <!--                        {:else}-->
                    <!--                            <tr>-->
                    <!--                                <td colspan="10" style="text-align: center">Ningún dato disponible en esta tabla-->
                    <!--                                </td>-->
                    <!--                            </tr>-->
                    <!--                        {/each}-->
                    <!--                        </tbody>-->
                    <!--                    </table>-->
                </div>
            </div>

            <div class="col-lg-12 mt-5">
                {#if listvigente.length > 0 || listvigente != '' }
                    {#if procesoactivo.length > 0 || procesoactivo != '' }

                        <h3 style="font-size: 19px;"><i class="fa fa-warning text-danger fs-3"></i> ¿Deseas generar un
                            reclamo de conformación del padrón electoral? <a class="btn btn-warning fs-5" on:click={() =>loadFormSolicitarInformacion(procesoactivo.pk)}
                                                                             href="javascript:void(0);"><i
                                    class="fe fe-plus-circle"></i> Llenar formulario</a></h3>

                        {#if soliprocesoactivos.length > 0 || soliprocesoactivos != '' }<br>
                            <table class='table table_danger table_striped'>
                                <thead>
                                <tr>
                                    <th></th>
                                    <th class="column-title text-left" style="width: 30%">Evento</th>
                                    <th class="column-title text-left" style="width: 40%">Observación</th>
                                    <th class="column-title text-center" style="width: 30%">Respuesta</th>
                                </tr>
                                </thead>
                                <tbody>
                                {#each soliprocesoactivos as p }
                                    <tr>
                                        <td></td>
                                        <td class="text-left">
                                            {p.cab.nombre}
                                        </td>
                                        <td class="text-left p-lg-5">
                                            <b>Categoría:</b> {p.tipo.display} <br>
                                            <b>Obs.</b> {p.observacion} <br>
                                            <b>F. Creación:</b> {p.fecha_creacion} <br>
                                            <b>Estado:</b>
                                            {#if p.estados == 0}
                                                <span className="text-primary">{p.estados_display}</span>
                                            {/if}
                                            {#if p.estados == 1}
                                                <span className="text-success">{p.estados_display}</span>
                                            {/if}
                                            {#if p.estados == 2}
                                                <span className="text-danger">{p.estados_display}</span>
                                            {/if}

                                        </td>
                                        <td class="text-left p-lg-5">
                                            {#if p.estados == 0}
                                                <span className="text-danger"><i className="fa fa-history"></i> Pendiente</span>

                                            {:else}
                                                <b>F. Validación:</b> {p.fechavalidacion}<br>
                                                <b>Resp.</b> {p.respuesta}
                                            {/if}
                                        </td>
                                    </tr>
                                {:else}
                                    <tr>
                                        <td colspan="10" style="text-align: center">NO EXISTEN NINGUN
                                            JUSTIFICATIVO
                                        </td>
                                    </tr>
                                {/each}

                                </tbody>
                            </table>
                        {/if}
                    {/if}

                {/if}
            </div>


        </div>

    {:else }
        <div class="mt-4 vh-100 row justify-content-center align-items-center propiedades">
            <div class="col-auto text-center">
                <Spinner color="primary" type="border" style="width: 3rem; height: 3rem;"/>
                <h3>Verificando la información, espere por favor...</h3>
            </div>
        </div>
    {/if}

</div>


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

{#if mOpenOffCanvasGenerico}
    <OffCanvasGenerico
            mToggle={mToggleOffCanvasGenerico}
            mOpen={mOpenOffCanvasGenerico}
            OffCanvasContent={modalDetalleOffCanvasContent}
            aData={aDataModal}
            placement={aplacement}
            {modalTitle}
            on:actionRun={actionRun}
    />
{/if}

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
