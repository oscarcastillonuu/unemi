<script lang="ts">
    import Swal from 'sweetalert2';
    import {variables} from '$lib/utils/constants';
    import {addToast} from '$lib/store/toastStore';
    import {browserGet, apiPOSTFormData, apiPOST, apiGET} from '$lib/utils/requestUtils';
    import {onMount} from 'svelte';
    import FilePond, {registerPlugin, supported} from 'svelte-filepond';
    import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
    import {loading} from '$lib/store/loadingStore';
    import {converToAscii, action_print_ireport} from '$lib/helpers/baseHelper';
    //import Input from '$components/Forms/Input.svelte'
    import {addNotification} from '$lib/store/notificationStore';
    import {Spinner, Tooltip} from 'sveltestrap';
    import {goto} from '$app/navigation';
    import {createEventDispatcher, onDestroy} from 'svelte';
    import type {Load} from '@sveltejs/kit';
    import {dndzone, overrideItemIdKeyNameBeforeInitialisingDndZones} from 'svelte-dnd-action';
    import {sumaValores} from "../alu_finanzas/_multiselect.svelte";

    const dispatch = createEventDispatcher();

    export let aData;
    export let mToggle;
    export let mOpen;
    let id = null;
    let eCronogramasFerias = [];
    let eParticipantesSearh = [];
    let eParticipantes = [];
    let cronograma_id = '0';
    let eTutores = [];
    let tutor_id = '';
    let resumen = '';
    let titulo = '';
    let objetivogeneral = '';
    let objetivoespecifico = '';
    let materiales = '';
    let resultados = '';
    let maxParticipantes = '';
    let minParticipantes = '';
    let propuestaArchivo = '';
    let pondPropuesta;
    let namePropuesta = 'filePropuesta';
    let busco = false;
    let ocultar = false;
    let eSolicitudFeria = {};
    let id_inscripcion = '';

    onMount(async () => {
        registerPlugin(FilePondPluginFileValidateType);
        id = aData.id;
        eSolicitudFeria = aData.eSolicitudFeria;
        eCronogramasFerias = aData.eCronogramasFerias;
        eTutores = aData.eTutores;
        ocultar = aData.ocultar;
        eParticipantes = aData.eParticipantes;
        propuestaArchivo = aData.eSolicitudFeria.docpropuesta;
        id_inscripcion = aData.id_inscripcion;
        maxParticipantes = eSolicitudFeria.cronograma.maxparticipantes;
        minParticipantes = eSolicitudFeria.cronograma.minparticipantes;
        if (Object.keys(eSolicitudFeria).length > 0) {
            cronograma_id = eSolicitudFeria.cronograma.id;
            tutor_id = eSolicitudFeria.tutor.id;
            resumen = eSolicitudFeria.resumen;
            titulo = eSolicitudFeria.titulo;
            objetivogeneral = eSolicitudFeria.objetivogeneral;
            objetivoespecifico = eSolicitudFeria.objetivoespecifico;
            materiales = eSolicitudFeria.materiales;
            resultados = eSolicitudFeria.resultados;
            pondPropuesta = FilePond.create(document.querySelector('.filepond'), {files: [eSolicitudFeria.docpropuesta]});
            // pondPropuesta = eSolicitudFeria.docpropuesta;
        }
    });

    // handle filepond events
    const handleInit = () => {
        console.log('FilePond has initialised');
    };

    const handleAddFile = (err, fileItem) => {
        console.log(pondPropuesta.getFiles());
        console.log('A file has been added', fileItem);
    };

    const searhParticipantes = async (e) => {
        e.preventDefault();
        console.log(e.target.value);
        eParticipantesSearh = [];
        if (e.target.value) {
            let participantes_excluir = eParticipantes.map((participante) => {
                return participante.idm;
            });
            console.log(participantes_excluir);
            const [res, errors] = await apiGET(fetch, 'alumno/ferias', {
                action: 'SearchParticipantes',
                search: e.target.value,
                cronograma_id: cronograma_id,
                participantes_excluir: JSON.stringify(participantes_excluir)
            });
            //loading.setLoading(false, 'Cargando, espere por favor...');
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
                    eParticipantesSearh = res.data.eParticipantesSearh;
                    if (eParticipantesSearh.length > 0) {
                        busco = true;
                    } else {
                        busco = false;
                    }
                    console.log(eParticipantesSearh);
                }
            }
        } else {
            eParticipantesSearh = [];
        }
    }
    const eliminarParticipante = (indice, participante) => {
        Swal.fire({
            html: `¿Está seguro de eliminar al participante <span class="badge bg-warning"> ${participante.nombre_completo}</span>?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'SI',
            cancelButtonText: 'NO',
        }).then((result) => {
            if (result.isConfirmed) {
                eParticipantes = eParticipantes.filter((car, ind) => {
                    return ind !== indice;
                });
                addToast({type: 'success', header: 'Exitoso', body: 'Elimino correctamente al participante'});
            } else {
                addToast({type: 'success', header: 'Notificación', body: 'Genial salvaste el registro'});
            }
        });
    }
    const seleccionarParticipante = (elemento, indice, participante) => {
        let input_searh = document.querySelector('.searh-participantes');
        let eParticipantesTemp = eParticipantes;
        let arreglo_ids = eParticipantesTemp.map((participante) => {
            return participante.idm;
        });
        if (arreglo_ids.indexOf(participante.idm)) {
            eParticipantesTemp.push(participante);
            eParticipantes = eParticipantesTemp;
        }
        eParticipantesSearh = [];
        input_searh.value = ''
    }

    const changeCronograma = async (id) => {
        if (id != 0) {
            const [res, errors] = await apiPOST(fetch, 'alumno/ferias', {
                action: 'consultarcronogramamaxmin',
                id: id
            });
            if (errors.length > 0) {
                errors.forEach((element) => {
                    addNotification({
                        msg: 'Error al cargar los datos',
                        type: 'error',
                        target: 'newNotificationToast'
                    });
                });
            } else {
                if (!res.isSuccess) {
                    addNotification({
                        msg: 'Error al cargar los datos',
                        type: 'error',
                        target: 'newNotificationToast'
                    });
                } else {
                    maxParticipantes = res.data['maxParticipantes']
                    minParticipantes = res.data['minParticipantes']
                }
            }
        }
    };

    const saveSolicitud = async (e) => {
        // alert('si')
        e.preventDefault();
        const $frmSolicitud = document.querySelector('#frmSolicitud');
        const formData = new FormData($frmSolicitud);
        let participantes = JSON.stringify(eParticipantes.map((participante) => {
            return participante.idm;
        }));
        // let aDataForm = {
        //      'id':id,
        //      'cronograma_id':cronograma_id,
        //      'tutor_id':tutor_id,
        //      'resumen':resumen,
        //      'titulo':titulo,
        //      'objetivogeneral':objetivogeneral,
        //      'objetivoespecifico':objetivoespecifico,
        //      'materiales':materiales,
        //      'resultados':resultados,
        //      'action':'saveSolicitudFeria',
        //      'docpresentacionpropuesta':pondPropuesta.getFiles()[0].file,
        //      'participantes':participantes
        // }
        formData.append('id', id)
        formData.append('action', 'saveSolicitudFeria')
        formData.append('participantes', participantes)
        if (!id) {
            let fileDocumento = pondPropuesta.getFiles();
            if (fileDocumento.length === 0) {
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
            if (pondPropuesta && pondPropuesta.getFiles().length > 0) {
                eFileDocumento = pondPropuesta.getFiles()[0];
            }
            formData.append('eFilePropuesta', eFileDocumento.file);
        } else {
            if (pondPropuesta.getFiles().length > 1) {
                addNotification({
                    msg: 'Archivo de documento debe ser único',
                    type: 'error',
                    target: 'newNotificationToast'
                });
                loading.setLoading(false, 'Cargando, espere por favor...');
                return;
            }
            let eFileDocumento = undefined;
            if (pondPropuesta && pondPropuesta.getFiles().length > 0) {
                eFileDocumento = pondPropuesta.getFiles()[0];
            }
            if (eFileDocumento) {
                formData.append('eFilePropuesta', eFileDocumento.file);
            }
        }

        if (!cronograma_id || cronograma_id === '0') {
            addNotification({
                msg: 'Favor complete el campo de Cronograma',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!tutor_id || tutor_id === 0) {
            addNotification({
                msg: 'Favor complete el campo de Tutor',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!titulo || titulo === '') {
            addNotification({
                msg: 'Favor complete el campo de Título',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!resumen || resumen === '') {
            addNotification({
                msg: 'Favor complete el campo de resumen',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!objetivogeneral || objetivogeneral === '') {
            addNotification({
                msg: 'Favor complete el campo de objetivo General',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!objetivoespecifico || objetivoespecifico === '') {
            addNotification({
                msg: 'Favor complete el campo de objetivo específicos',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!materiales || materiales === '') {
            addNotification({
                msg: 'Favor complete el campo de materiales',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (!resultados || resultados === '') {
            addNotification({
                msg: 'Favor complete el campo de materiales',
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        console.log(eParticipantes)
        if (eParticipantes.length < minParticipantes) {
            addNotification({
                msg: `Debe agregar minimo ${minParticipantes} participantes`,
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }
        if (eParticipantes.length > maxParticipantes) {
            addNotification({
                msg: `Supera el máximo de participantes: ${maxParticipantes}`,
                type: 'error',
                target: 'newNotificationToast'
            });
            return;
        }

        loading.setLoading(true, 'Guardando la información, espere por favor...');
        const [res, errors] = await apiPOSTFormData(fetch, 'alumno/ferias', formData);

        if (errors.length > 0) {
            addToast({type: 'error', header: 'Ocurrio un error', body: errors[0].error});
            loading.setLoading(false, 'Cargando, espere por favor...');
            return;
        } else {
            if (!res.isSuccess) {
                addToast({type: 'error', header: 'Ocurrio un error', body: res.message});
                if (!res.module_access) {
                    goto('/');
                }
                loading.setLoading(false, 'Cargando, espere por favor...');
                return;
            } else {
                addToast({type: 'success', header: 'Exitoso', body: 'Se guardo correctamente los datos'});
                loading.setLoading(false, 'Cargando, espere por favor...');
                dispatch('actionRun', {action: 'nextProccess', value: 1});
                return;

            }
        }
    }

</script>
<form id="frmSolicitud" enctype="multipart/form-data" on:submit={saveSolicitud}>
    <div class="card-body">
        {#if !ocultar}
            <div class="row g-3">
                <div class="col-md-12">
                    <label for="eCronogramaFeria" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Cronograma:
                    </label>
                    <select class="form-control form-select" id="eCronogramaFeria" name="eCronogramaFeria"
                            bind:value={cronograma_id} on:change={({ target: { value } }) => changeCronograma(value)}>
                        <option value=0>---------</option>
                        {#each eCronogramasFerias as cronograma }
                            <option value={cronograma.id}>
                                {cronograma.display}
                            </option>
                        {/each}
                    </select>
                </div>
                <!--                <span>{eTutores.length}</span>-->
                <div class="col-md-12">
                    <label for="eTutor" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Tutor:
                    </label>
                    <select class="form-control form-select" name="eTutor" id="eTutor" bind:value={tutor_id}>
                        <option value=0>---------</option>
                        {#each eTutores as tutor }
                            <option value={tutor.id}>
                                {tutor.display}
                            </option>
                        {/each}
                    </select>
                </div>
                <div class="col-md-12">
                    <label for="titulo" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Título:
                    </label>
                    <textarea
                            type="text"
                            class="form-control"
                            id="titulo"
                            name="titulo"
                            cols="30"
                            rows="2" bind:value={titulo}
                    />
                </div>
                <div class="col-md-12">
                    <label for="resumen" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Resumen:
                    </label>
                    <textarea
                            type="text"
                            class="form-control"
                            id="resumen"
                            name="resumen"
                            cols="30"
                            rows="4"
                            bind:value={resumen}
                    />
                </div>
                <div class="col-md-12">
                    <label for="objetivogeneral" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Objetivo General:
                    </label>
                    <textarea
                            type="text"
                            class="form-control"
                            id="objetivogeneral"
                            name="objetivogeneral"
                            cols="30" rows="3"
                            bind:value={objetivogeneral}
                    />
                </div>
                <div class="col-md-12">
                    <label for="objetivoespecifico" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Objetivo Específicos:
                    </label>
                    <textarea
                            type="text"
                            class="form-control"
                            id="objetivoespecifico"
                            name="objetivoespecifico"
                            cols="30" rows="3"
                            bind:value={objetivoespecifico}
                    />
                </div>
                <div class="col-md-12">
                    <label for="materiales" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Materiales:
                    </label>
                    <textarea
                            type="text"
                            class="form-control"
                            id="materiales"
                            name="materiales"
                            cols="30" rows="2"
                            bind:value={materiales}
                    />
                </div>
                <div class="col-md-12">
                    <label for="resultados" class="form-label fw-bold">
                        <i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Resultados:
                    </label>
                    <textarea
                            type="text"
                            class="form-control"
                            id="resultados"
                            name="resultados"
                            cols="30" rows="2"
                            bind:value={resultados}
                    />
                </div>
                <div class="col-md-12">
                    <label for="ePropuestaFileDocumento" class="form-label fw-bold"
                    ><i title="Campo obligatorio" class="bi bi-exclamation-circle-fill" style="color: red"></i>
                        Documento de Presentación:</label
                    >
                    <FilePond
                            id="ePropuestaFileDocumento"
                            class="pb-0 mb-0"
                            bind:this={pondPropuesta}
                            {namePropuesta}
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
                    <br/>
                    <small class="text-warning">Tamaño máximo permitido 15Mb, en formato pdf</small><br>
                    {#if propuestaArchivo != '' && propuestaArchivo != null}
                        <label for="archivoactual" class="form-label fw-bold"
                        ><i title="Archivo Actual" class="bi bi-exclamation-circle-fill" style="color: #b6d4fe"></i>
                            Documento Actual: &nbsp;</label
                        ><a class="btn btn-info btn-sm"
                            id="archivoactual"
                            title="VER PROPUESTA"
                            href="{propuestaArchivo}"
                            target="_blank"> <i class="bi bi-file-arrow-down-fill"></i></a
                    ><br/>
                    {/if}
                    <!--                    <small class="text-warning">{ eParticipantes.length }</small>-->
                    <!--                    <small class="text-warning">{ minParticipantes } - { maxParticipantes }</small>-->
                </div>
            </div>
            {#if cronograma_id != '0'}
                <div class="row mt-2 pb-4" style="background-color: rgb(239, 239, 239);">
                    <!--{#if eParticipantes.length < 5}-->
                    <div class="col-md-12">
                        <div class="{ eParticipantesSearh.length > 0 ? 'wrapper' : 'wrapper-temp'}">
                            <div class="search-input { eParticipantesSearh.length > 0 || busco ? 'active' : ''} ">
                                <a href="" target="_blank" hidden></a>
                                <input type="text" class="form-control mb-4 mt-4 searh-participantes"
                                       placeholder="Buscar  participantes" on:keyup={searhParticipantes}>
                                <ul class="autocom-box">
                                    {#each eParticipantesSearh as participante, index}
                                        <li class="list-group-item px-0 pt-2 "
                                            on:click={() => seleccionarParticipante(this, index, participante)}>
                                            <div class="row">
                                                <div class="col-auto">
                                                    <div class="avatar avatar-md">
                                                        <img alt="" src="{participante.foto}" class="rounded-circle">
                                                    </div>
                                                </div>
                                                <div class="col ms-n3">
                                                    <h4 class="mb-0 h5">{participante.nombre_completo}</h4>
                                                    <span class="me-2 fs-6">
                                                    <span class="text-dark  me-1 fw-semi-bold">{participante.nivel}</span>
                                                </span>
                                                    <span class="me-2 fs-6">
                                                    <span class="badge bg-success">{participante.carrera}</span>
                                                </span>
                                                    <span class="fs-6">
                                                </span>
                                                </div>
                                                <div class="col-auto">
                                                </div>
                                            </div>
                                        </li>
                                    {:else}
                                        <!-- {#if busco}
                                            <li class="text-align">No existen participantes</li>
                                        {/if} -->
                                    {/each}
                                </ul>
                                <div class="icon"><i class="fe fe-search"></i></div>
                            </div>
                        </div>
                    </div>
                    <!--{/if}-->
                    <div class="col-md-12">
                        <ul class="list-group list-group-flush" style="border-radius: 5px ;">
                            {#each eParticipantes as participante, index}
                                <li class="list-group-item px-0 pt-2">
                                    <div class="row pt-2">
                                        <div class="col-auto">
                                            <div class="avatar avatar-md">
                                                <img alt="" src="{participante.foto}" class="rounded-circle">
                                            </div>
                                        </div>
                                        <div class="col ms-n3">
                                            <h4 class="mb-0 h5">{participante.nombre_completo}</h4>
                                            <span class="badge bg-primary">{participante.carrera}</span>
                                            <span class="me-2 fs-6">

                                            <span class="badge bg-success">{participante.nivel}</span>
                                        </span>
                                            <span class="me-2 fs-6">
                                        </span>
                                            <span class="fs-6">
                                        </span><br>

                                            <b>{participante.tipo_documento}:</b> {participante.documento}
                                            <b>Email:</b>{participante.lista_emails}
                                        </div>
                                        <div class="col-auto pt-2 pl-4">
                                            {#if participante.id != id_inscripcion}
                                                <a on:click={() => eliminarParticipante(index, participante)}>
                                                    <i class="fe fe-trash dropdown-item-icon "></i>
                                                </a>
                                            {/if}
                                        </div>
                                    </div>
                                </li>
                            {:else}
                                <li class="list-group-item px-0 pt-2  text-center">
                                    <!-- <div class="row"> -->
                                    No existen participantes seleccionados
                                    <!-- </div> -->
                                </li>
                            {/each}
                        </ul>
                    </div>
                </div>
            {/if}
        {:else}

            <ul class="nav nav-tabs" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="home-tab" data-bs-toggle="tab" data-bs-target="#home"
                            type="button" role="tab" aria-controls="home" aria-selected="true"><b>INFORMACIÓN DEL
                        PROYECTO</b></button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="colaboradores-tab" data-bs-toggle="tab" data-bs-target="#colaboradores"
                            type="button" role="tab" aria-controls="colaboradores" aria-selected="false"><b>COLABORADORES
                        DEL PROYECTO</b></button>
                </li>
            </ul>
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="home" role="tabpanel" aria-labelledby="home-tab">
                    <div class="row">
                        <div class="col-md-12">
                            <div class=" mb-4" id="ecommerceAccordion">
                                <!-- List group -->
                                <ul class="list-group list-group-flush">
                                    <!-- List group item -->
                                    <li class="list-group-item px-0">
                                        <!-- Toggle -->
                                        <a class="d-flex align-items-center text-inherit text-decoration-none fw-semi-bold mb-0 collapsed"
                                           data-bs-toggle="collapse" href="#productDetails" role="button"
                                           aria-expanded="false" aria-controls="productDetails">
                                            <div class="me-auto">
                                                INFORMACIÓN DEL PROYECTO
                                            </div>
                                            <!-- Chevron -->
                                            <span class="chevron-arrow  ms-4">
                                    <i class="fe fe-chevron-down fs-4"></i>
                                  </span>
                                        </a>
                                        <!-- Row -->
                                        <!-- Collapse -->
                                        <div class="collapse" id="productDetails" data-bs-parent="#ecommerceAccordion"
                                             style="">
                                            <div class="py-3 ">
                                                <h4>TÍTULO DEL PROYECTO:</h4>
                                                <p>{eSolicitudFeria.titulo}</p>
                                                <h4>RESUMEN DE LA PROPUESTA:</h4>
                                                <p>{eSolicitudFeria.resumen}</p>
                                            </div>
                                        </div>
                                    </li>
                                    <!-- List group item -->
                                    <li class="list-group-item px-0">
                                        <!-- Toggle -->
                                        <a class="d-flex align-items-center text-inherit text-decoration-none fw-semi-bold mb-0 collapsed"
                                           data-bs-toggle="collapse" href="#specifications" role="button"
                                           aria-expanded="false" aria-controls="specifications">
                                            <div class="me-auto">
                                                OBJETIVOS
                                            </div>
                                            <!-- Chevron -->
                                            <span class="chevron-arrow  ms-4">
                                    <i class="fe fe-chevron-down fs-4"></i>
                                  </span>
                                        </a>
                                        <!-- Row -->
                                        <!-- Collapse -->
                                        <div class="collapse" id="specifications" data-bs-parent="#ecommerceAccordion"
                                             style="">
                                            <div class="py-3 ">
                                                <h4>OBJETIVO GENERAL:</h4>
                                                <p>{eSolicitudFeria.objetivogeneral}</p>
                                                <h4>OBJETIVOS ESPECÍFICOS: </h4>
                                                <p>{eSolicitudFeria.objetivoespecifico}</p>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="list-group-item px-0">
                                        <!-- Toggle -->
                                        <a class="d-flex align-items-center text-inherit text-decoration-none fw-semi-bold mb-0 collapsed"
                                           data-bs-toggle="collapse" href="#freeShippingPolicy" role="button"
                                           aria-expanded="false" aria-controls="freeShippingPolicy">
                                            <div class="me-auto">
                                                MATERIALES E INSTRUMENTOS A UTILIZAR:
                                            </div>
                                            <!-- Chevron -->
                                            <span class="chevron-arrow  ms-4">
                                    <i class="fe fe-chevron-down fs-4"></i>
                                  </span>
                                        </a>
                                        <!-- Row -->
                                        <!-- Collapse -->
                                        <div class="collapse" id="freeShippingPolicy"
                                             data-bs-parent="#ecommerceAccordion" style="">
                                            <div class="py-3 ">
                                                <p class="mb-0">{eSolicitudFeria.materiales}</p>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="list-group-item px-0 border-bottom">
                                        <!-- Toggle -->
                                        <a class="d-flex align-items-center text-inherit text-decoration-none fw-semi-bold mb-0 collapsed"
                                           data-bs-toggle="collapse" href="#refundPolicy" role="button"
                                           aria-expanded="false" aria-controls="refundPolicy">
                                            <div class="me-auto">
                                                DETALLES DE LOS RESULTADOS A ESPERAR
                                            </div>
                                            <!-- Chevron -->
                                            <span class="chevron-arrow  ms-4">
                                    <i class="fe fe-chevron-down fs-4"></i>
                                  </span>
                                        </a>
                                        <!-- Row -->
                                        <!-- Collapse -->
                                        <div class="collapse " id="refundPolicy" data-bs-parent="#ecommerceAccordion">
                                            <div class="py-3 ">
                                                <p class="mb-0">{eSolicitudFeria.resultados}</p>

                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="tab-pane fade" id="colaboradores" role="tabpanel" aria-labelledby="colaboradores-tab">
                    <div class="table-responsive overflow-y-hidden">
                        <table class="table mb-0 text-nowrap mt-3">
                            <thead class="table-light">
                            <tr>
                                <th colspan="4"><b>Tutor:</b> {eSolicitudFeria.tutor.display}</th>
                            </tr>
                            <tr>
                                <th scope="col" class="border-top-0">Estudiante</th>
                                <th scope="col" class="border-top-0 ">Carrera</th>
                                <th scope="col" class="border-top-0 ">Semestre</th>
                            </tr>
                            </thead>
                            <tbody>
                            {#each eParticipantes as participante, index}
                                <tr>
                                    <td class="align-middle">
                                        <div class="d-flex align-items-center">
                                            <div class="avatar avatar-sm">
                                                <img src="{participante.foto}" alt="" class="rounded-circle">
                                            </div>
                                            <div class="ms-2">
                                                <h5 class="mb-0">{participante.nombre_completo} </h5>
                                                <b>Ced.:</b> {participante.documento}
                                                {#each participante.lista_emails as email}
                                                    <span class="badge badge-success">{email}</span>
                                                {/each}
                                            </div>
                                        </div>
                                    </td>
                                    <td class="align-middle ">
                                        {participante.carrera}
                                    </td>
                                    <td class="align-middle ">
                                        {participante.nivel}
                                    </td>
                                </tr>
                            {/each}

                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        {/if}
    </div>
    <div class="card-footer text-muted">
        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
            <!--<button class="btn btn-primary me-md-2" type="button">Button</button>-->
            {#if !ocultar}
                <button type="submit" class="btn btn-info">Guardar</button>
            {/if}
            <a color="danger" class="btn  { ocultar ? 'btn-info' : 'btn-danger '}" on:click={() => mToggle()}>
                {#if ocultar}Cerrar{:else}Cancelar{/if}
            </a>
        </div>
    </div>
</form>

<style>
    @import 'filepond/dist/filepond.css';

    .wrapper-temp .search-input {
        background: #fff;
        width: 100%;
        height: 45px;
        border-radius: 5px;
        position: relative;
        box-shadow: 0px 1px 5px 4px rgba(0, 0, 0, 0.12);
        margin-bottom: 20px;
    }

    .wrapper .search-input {
        background: #fff;
        width: 100%;
        border-radius: 5px;
        position: relative;
        box-shadow: 0px 1px 5px 4px rgba(0, 0, 0, 0.12);
    }

    .search-input input {
        height: 45px;
        width: 100%;
        outline: none;
        border: none;
        border-radius: 5px;
        padding: 0 50px 0 20px;
        font-size: 14px;
        box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.1);
    }

    .search-input.active input {
        border-radius: 5px 5px 0 0;
    }

    .search-input .autocom-box {
        padding: 0;
        opacity: 0;
        pointer-events: none;
        max-height: 280px;
        overflow-y: auto;
    }

    .search-input.active .autocom-box {
        padding: 10px 8px;
        opacity: 1 !important;
        pointer-events: auto;
    }

    .autocom-box li {
        list-style: none;
        padding: 8px 12px;
        display: none;
        width: 100%;
        cursor: default;
        border-radius: 3px;
    }

    .search-input.active .autocom-box li {
        display: block;
    }

    .autocom-box li:hover {
        background: #efefef;
    }

    .search-input .icon {
        position: absolute;
        right: 0px;
        top: 0px;
        height: 55px;
        width: 55px;
        text-align: center;
        line-height: 55px;
        font-size: 20px;
        color: #644bff;
        cursor: pointer;
    }

</style>
