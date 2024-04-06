<script context="module" lang="ts">
    import type { Load } from '@sveltejs/kit';
    export const load: Load = async ({ fetch }) => {
        let ePeriodoEventos = [];
        let eEventos = [];
        let ePersona = {};
        const ds = browserGet('dataSession');
        //console.log(ds);
        if (ds != null || ds != undefined) {
            loading.setLoading(true, 'Cargando, espere por favor...');
            const [res, errors] = await apiGET(fetch, 'alumno/evento', {opc_select:2});
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
                    ePeriodoEventos = res.data['ePeriodosEventos'];
                    eEventos = res.data['eEventos'];
                    ePersona = res.data['ePersona'];
                }
            }
        }

        return {
            props: {
                ePeriodoEventos,
                eEventos,
                ePersona
            }
        };
    };
</script>
<script lang="ts">
    import { addToast } from "$lib/store/toastStore";
    import { apiPOSTFormData, apiPOST, browserGet, apiGET} from "$lib/utils/requestUtils";
    import Swal from 'sweetalert2';
    import { onMount } from 'svelte';
    import { variables } from '$lib/utils/constants';
    import { Card, CardBody, Col, Row, Nav, NavItem } from 'sveltestrap';
    import BreadCrumb from '$components/BreadCrumb/BreadCrumb.svelte';
    import CardEvento  from '$components/Alumno/Evento/Card.svelte'
    import { loading } from '$lib/store/loadingStore';
    import { createEventDispatcher, onDestroy } from 'svelte';


    const dispatch = createEventDispatcher();
    import { goto } from '$app/navigation';
    import { navigating } from '$app/stores';
    import { addNotification } from '$lib/store/notificationStore';
    import { Modal, ModalBody, ModalHeader } from 'sveltestrap';
    import {FilePondFile} from "filepond";

    let itemsBreadCrumb = [{ text: 'Eventos', active: true, href: undefined }];
    let backBreadCrumb = { href: '/', text: 'Atrás' };
    $: loading.setNavigate(!!$navigating);
    $: loading.setLoading(!!$navigating, 'Cargando, espere por favor...');
    export  let ePeriodoEventos;
    export  let eEventos;
    export  let ePersona;
    console.log(eEventos);
    console.log(ePersona);
    let num_active = 2;
    const action_init_load = async (opc_select) => {
        const ds = browserGet('dataSession');
        //console.log(ds);
        if (ds != null || ds != undefined) {
            loading.setLoading(true, 'Cargando, espere por favor...');
            const [res, errors] = await apiGET(fetch, 'alumno/evento', {opc_select:opc_select});
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
                    ePeriodoEventos = res.data['ePeriodosEventos'];
                    eEventos = res.data['eEventos'];
                    ePersona = res.data['ePersona'];
                }
            }
        }
        num_active = opc_select;
    }
</script>
<BreadCrumb title="Eventos" items={itemsBreadCrumb} back={backBreadCrumb} />
<Row>
    <Col class="col-md-3">
        <Card class="mb-4">
            <CardBody class="p-0">
                <div class="pt-16 rounded-top-md" style="
								background: url(../assets/images/background/profile-bg.jpg) no-repeat;
								background-size: cover;
							"></div>
                <div class="text-center">
                    <img src="{ePersona.foto_perfil}" onerror="this.onerror=null;this.src='./image.png'" class="mt-n12 rounded-circle avatar-xl mb-3 border border-4 border-white" alt="" style="width: 12em; height: 12em;">
                    <h4 class="mb-0">{ePersona.apellido1} {ePersona.apellido2}</h4>
                    <h4 class="mb-0">{ePersona.nombres}</h4>
                </div>
                <div class="p-2">
                    <Row class="border-top mt-1 border-bottom mb-1 g-0">
                        <Col>
                            <div class="pe-1 ps-3 py-2">
                                <h5 class="mb-0">{ePersona.numero_pendiente}</h5>
                                <span>Pendiente</span>
                            </div>
                        </Col>
                        <Col class="border-start">
                            <div class="pe-1 ps-2 py-2">
                                <h5 class="mb-0">{ePersona.numero_asistire}</h5>
                                <span>Asistiré</span>
                            </div>
                        </Col>
                        <Col class="border-start">
                            <div class="pe-1 ps-3 py-2">
                                <h5 class="mb-0">{ePersona.numero_no_asistire}</h5>
                                <span>No Asistiré</span>
                            </div>
                        </Col>
                    </Row>
                    <div class="d-flex  border-bottom py-1 mt-0">
                        <span><i class="bi bi-telephone"></i></span>
                        <span class="text-dark px-2 fs-6 text-muted">{#if ePersona.telefono_conv}{ePersona.telefono_conv}{:else}No definido{/if}</span>
                    </div>
                    <div class="d-flex  border-bottom py-1 mt-0">
                        <span><i class="bi bi-phone"></i></span>
                        <span class="text-dark px-2 fs-6 text-muted">{#if ePersona.telefono}{ePersona.telefono}{:else}No definido{/if}</span>
                    </div>
                    <div class="d-flex  border-bottom py-1 mt-0">
                        <span><i class="bi bi-envelope"></i></span>
                        <span class="text-dark px-2 fs-6 text-muted">{ePersona.emailinst}, {ePersona.email}</span>
                    </div>
                    <div class="d-flex border-bottom py-1 mt-0">
                        <i class="bi bi-geo-alt"></i>
                        <span class="text-dark px-2 fs-6 text-muted">{ePersona.direccion_corta}</span>
                    </div>
                </div>
            </CardBody>
        </Card>
    </Col>
    <Col class="col-md-9">
        <Nav class="nav-lb-tab" id="tab" role="tablist">
            <NavItem>
                <a class="nav-link {num_active === 2?'active':''}" on:click={()=> action_init_load(2)}>
                    <i class="fe fe-calendar nav-icon"></i> Mis Eventos
                </a>
            </NavItem>
            <NavItem>
                <a class="nav-link {num_active === 1?'active':''}" on:click={()=> action_init_load(1)}>
                    <i class="fe fe-credit-card nav-icon"></i> Eventos Disponibles
                </a>
            </NavItem>
        </Nav>
        <Row class="mt-2">

            {#each eEventos as eEvento}
                <Col class="col-xl-4 col-lg-6 col-md-6 col-12">
                    <CardEvento image="{eEvento.imagen}" url="/alu_eventos/{eEvento.id}" title="{eEvento.display}">
                        <div slot="card-body">
                            <h3 class="mb-2 text-wrap" >
                                <a href="/alu_eventos/{eEvento.id}" class="text-wrap" style="height:10rem;">{eEvento.evento.display}</a>
                            </h3>
                            <!-- List -->
                            <ul class="mb-0 list-unstyled">
                                <li class="list-item">
                                    {#if eEvento.inscrito.estado_confirmacion == 0}
                                        <span class="badge bg-warning">PENDIENTE DE CONFIRMAR ASISTENCIA</span>
                                    {:else if eEvento.inscrito.estado_confirmacion == 1}
                                        <span class="badge bg-success">ASISTIRÉ</span>
                                    {:else if eEvento.inscrito.estado_confirmacion == 1}
                                        <span class="badge bg-danger">NO ASISTIRÉ</span>
                                    {/if}

                                </li>
                                <li class="list-item">
                                    <i class="mdi mdi-calendar text-muted me-1"></i>{eEvento.inscrito.fecha_creacion}
                                </li>
                                <li class="list-item">
                                    <i class="mdi mdi-tag text-muted me-1"></i>  {eEvento.tipo.nombre}
                                </li>
                            </ul>
                        </div>
                    </CardEvento>
                </Col>
            {/each}
            {#each ePeriodoEventos as ePeriodoEvento}
                <Col class="col-xl-4 col-lg-6 col-md-6 col-12">
                    <CardEvento image="{ePeriodoEvento.imagen}" url="/alu_eventos/{ePeriodoEvento.id}">
                        <div slot="card-body">
                            <h3 class="mb-2 text-wrap" >
                                <a href="/alu_eventos/{ePeriodoEvento.id}" class="text-wrap">{ePeriodoEvento.evento.nombre}</a>
                            </h3>
                            <p class="text-wrap">
                                <i class="mdi mdi-menu text-muted me-1"></i> {ePeriodoEvento.descripcionbreve}
                            </p>
                            <!-- List -->
                            <ul class="mb-0 list-unstyled">
                                <li class="list-item">
                                    <i class="mdi mdi-calendar text-muted me-1"></i>{ePeriodoEvento.fechainicio} - {ePeriodoEvento.fechafin}
                                </li>
                                <li class="list-item">
                                    <i class="mdi mdi-clock text-muted me-1"></i>{ePeriodoEvento.horainicio} - {ePeriodoEvento.horafin}
                                </li>
                                <li class="list-item">
                                    <i class="mdi mdi-tag text-muted me-1"></i>  {ePeriodoEvento.tipo.nombre}
                                </li>
                            </ul>
                        </div>
                    </CardEvento>
                </Col>
            {/each}
        </Row>
    </Col>
</Row>
<style global>
    @import '/static/assets/libs/@mdi/font/css/materialdesignicons.min.css';
    @import '/static/assets/css/theme.min.css';
</style>