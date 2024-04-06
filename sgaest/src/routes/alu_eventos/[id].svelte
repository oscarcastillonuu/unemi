<script context="module" lang="ts">
    import type { Load } from '@sveltejs/kit';
    import { session, page, navigating } from '$app/stores';
    export const load: Load = async ({ params, fetch }) => {
        const id = params.id;
        const ds = browserGet('dataSession');
        let eEvento = {};
        if (ds != null || ds != undefined) {
            const dataSession = JSON.parse(ds);
            const [res, errors] = await apiGET(fetch, 'alumno/evento', {
                action: 'getEvent',
                id: id
            });
            if (errors.length > 0) {
                addToast({ type: 'error', header: 'Ocurrio un error', body: errors[0].error });
                return {
                    status: 302,
                    redirect: '/'
                };
            } else {
                if (!res.isSuccess) {
                    addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
                    if (!res.module_access) {
                        return {
                            status: 302,
                            redirect: '/'
                        };
                    }
                } else {
                    console.log(res.data);
                    eEvento = res.data.eEvento;
                }
            }
        } else {
            return {
                status: 302,
                redirect: '/alu_eventos'
            };
        }

        return {
            props: {
                eEvento
            }
        };
    };
</script>
<script lang="ts">
    import { apiGET, apiPOST, browserGet, browserSet } from '$lib/utils/requestUtils';
    import { loading } from '$lib/store/loadingStore';
    import { onMount } from 'svelte';
    import EventoDetalle  from '$components/Alumno/Evento/EventoDetalle.svelte';
    import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
    import {loading} from "$lib/store/loadingStore";
    import {onMount} from "svelte";
    import Swal from "sweetalert2";
    import {addToast} from "$lib/store/toastStore";
    import {Row} from "sveltestrap";
    export let eEvento;
    let itemsBreadCrumb = [
        { text: 'Eventos', active: false, href: '/alu_eventos' },
        { text: `${eEvento.evento.nombre}`, active: true, href: undefined }
    ];
    let backBreadCrumb = { href: '/alu_eventos', text: 'Atrás' }
    $: loading.setNavigate(!!$navigating);
    $: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
    onMount(async () => {});


    const actionRun = (event) => {
        /*if (event.detail.action === 'totalPedidos'){
            total_pedidos = event.detail.value;
        }*/
    };
    const inscribirseEvento = (eEvento, asiste=false) =>{
        let texto  = asiste ?`¿Está seguro que desea inscribirse en este evento?`:`Está a punto de inscribirse, confirmando su participación en el evento. ¿Está seguro que desea continuar?`;
        const mensaje = {
            html: `<b>${texto}</b>`,
            //html: `Esta acción es irreversible`,
            type: 'warning',
            icon: 'warning',
            showCancelButton: true,
            allowOutsideClick: false,
            confirmButtonColor: '#FE9900',
            //cancelButtonColor: '#d33',
            confirmButtonText: `Si, deseo hacerlo!`,
            cancelButtonText: 'No, cancelar'
        };
        Swal.fire(mensaje)
            .then(async (result) =>{
                if(result.value){
                    loading.setLoading(true, 'Cargando, espere por favor...');
                    const [res, errors] = await apiPOST(fetch, 'alumno/evento', {
                        action: 'registerEvent',
                        id: eEvento.id,
                        asiste:asiste
                    });
                    if (errors.length > 0) {
                        errors.forEach((element) => {
                            addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
                        });
                    } else {
                        if (!res.isSuccess) {
                            addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
                        } else {
                            addToast({
                                type: 'success',
                                header: 'Exitoso!',
                                body: 'Se elimino correctamente la encuesta'
                            });
                            action_init_load(eEvento.id);
                        }
                    }
                    loading.setLoading(false, 'Cargando, espere por favor...');
                }
            });
    }
    const inscribirseAsistenciaEvento = (eEvento, tipo) =>{
        let texto  = tipo == 1 ?`confirmar`:`declinar`;
        texto = `Está a punto de ${texto} su asistencia al evento.\n¿Desea continuar?`;
        const mensaje = {
            html: `<b>${texto}</b>`,
            //html: `Esta acción es irreversible`,}
            customClass: {
                cancelButton: 'btn-mini',
                confirmButton: 'btn-confirm',
            },
            type: 'warning',
            icon: 'warning',
            showCancelButton: true,
            allowOutsideClick: false,
            confirmButtonColor: '#FE9900',
            //cancelButtonColor: '#d33',
            confirmButtonText: `Si, deseo hacerlo!`,
            cancelButtonText: 'No, cancelar'
        };
        Swal.fire(mensaje)
            .then(async (result) =>{
                if(result.value){
                    loading.setLoading(true, 'Cargando, espere por favor...');
                    const [res, errors] = await apiPOST(fetch, 'alumno/evento', {
                        action: 'confirmAssistance',
                        id: eEvento.inscrito.id,
                        tipo:tipo
                    });
                    if (errors.length > 0) {
                        errors.forEach((element) => {
                            addToast({ type: 'error', header: 'Ocurrio un error', body: element.error });
                        });
                    } else {
                        if (!res.isSuccess) {
                            addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
                        } else {
                            addToast({
                                type: 'success',
                                header: 'Exitoso!',
                                body: res.data.msg
                            });
                            action_init_load(eEvento.id);
                        }
                    }
                    loading.setLoading(false, 'Cargando, espere por favor...');
                }
            });
    }
    const action_init_load = async (evento_id) => {
        const ds = browserGet('dataSession');
        //console.log(ds);
        if (ds != null || ds != undefined) {
            loading.setLoading(true, 'Cargando, espere por favor...');
            const [res, errors] = await apiGET(fetch, 'alumno/evento', {
                action: 'getEvent',
                id:evento_id,
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
                    addToast({ type: 'error', header: 'Ocurrio un error', body: res.message });
                    if (!res.module_access) {
                        return {
                            status: 302,
                            redirect: '/'
                        };
                    }
                } else {
                    eEvento = res.data['eEvento'];
                }
            }
        }
    }
</script>
<BreadCrumb title="" items={itemsBreadCrumb} back={backBreadCrumb} />
<EventoDetalle title="{eEvento.evento.nombre}" image="{eEvento.imagen}" front_page="{eEvento.portada}" url_video="" short_description="{eEvento.descripcionbreve}">
    <div slot="card-body-content">
        {@html eEvento.cuerpo}
        {#if eEvento.iframemapa}
            <h3><b><i class="mdi mdi-map-marker"></i> Ubicación del Evento</b></h3>
            <Row>
                {@html eEvento.iframemapa}
            </Row>
        {/if}
    </div>
    <div slot="card-body-content2">
        <div class="mb-1">
            <span class="text-muted fw-bold"><i class="mdi mdi-calendar text-muted me-1"></i>{eEvento.fechainicio} - {eEvento.fechafin}</span>
        </div>
        <div class="mb-1">
            <span class="text-muted fw-bold"><i class="mdi mdi-clock text-muted me-1"></i>  {eEvento.horainicio} - {eEvento.horafin}</span>
        </div>
        <div class="mb-3">
            <span class="text-muted fw-bold"><i class="mdi mdi-tag text-muted me-1"></i>  {eEvento.tipo.nombre}</span>
        </div>
        {#if !eEvento.cerrado && eEvento.publicar }
            {#if Object.keys(eEvento.inscrito).length > 0}
                {#if eEvento.no_confirme}
                    <div class="text-center">
                        <h4 style="margin-bottom: 12px">¿Asistirás?</h4>
                        <a class="btn btn-sm btn-mini transition-3d-hover" on:click={()=>{inscribirseAsistenciaEvento(eEvento, 1)}} style="color:white;background-color: #faa732; width: 40%;  border-radius: 3.2rem; font-size: 15px">
                            <i class="mdi mdi-check"></i> Si
                        </a>
                        <a class="btn  btn-outline-secondary btn-mini transition-3d-hover" on:click={()=>{inscribirseAsistenciaEvento(eEvento, 2)}} style="width: 40%;  border-radius: 3.2rem; font-size: 15px">
                            <i class="mdi mdi-close"></i> No
                        </a>
                    </div>
                {/if}
            {:else}
                <div class="d-grid">
                    <a class="btn btn-primary  mb-2 btn-sm" on:click={()=>inscribirseEvento(eEvento)}><i class="mdi mdi-plus-circle"></i> Inscribirme</a>
                    <a class="btn btn-outline-primary btn-sm" on:click={()=>inscribirseEvento(eEvento, true)}><i class="mdi mdi-calendar-plus"></i> Inscribirme y Confirmar Asistencia</a>
                </div>
            {/if}
        {/if}
    </div>
</EventoDetalle>
<style>
    .btn-confirm{
        color:white;
        background-color: #faa732;
        width: 40%;
        border-radius: 3.2rem;
        font-size: 15px
    }
    .btn-mini{
        padding-top: 3px;
        padding-bottom: 3px;
        padding-left: 3px;
        padding-right: 3px;
        font-size: 10.5px;
        -webkit-border-radius: 3px;
        -moz-border-radius: 3px;
        border-radius: 3px;
    }
    .transition-3d-hover, .animate-this {
        transition: all 0.2s ease-in-out;
    }

    .transition-3d-hover, .animate-this {
        transition: all 0.2s ease-in-out;
    }
</style>