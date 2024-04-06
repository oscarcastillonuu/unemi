<script lang="ts">
    import { browserGet, apiPOST, apiGET } from '$lib/utils/requestUtils';
	import { loading } from '../../lib/store/loadingStore';
	import ModalGenerico from '../../components/Alumno/Modal.svelte';
	import { addNotification } from '../../lib/store/notificationStore';

    import ModalGrupo from './_modalGrupo.svelte';
    import { createEventDispatcher } from 'svelte';
    let aDataModal = {};
	let aplacement = '';
	let modalDetalleOffCanvasContent;
	let modalDetalleContent;
	let mOpenModalGenerico = false;
	let mOpenOffCanvasGenerico = false;
	let modalTitle = '';
    export let ePeriodo;
    export let idiomas;
    export let cursa_modulo_de_ingles;
    export let mis_gruposInscripcion;
    const dispatch = createEventDispatcher();
	function actionRun(event) {
        loading.setLoading(true, 'Cargando, espere por favor...');
        mOpenModalGenerico = false;
          let idList = mis_gruposInscripcion.map(obj => obj.grupo.periodo.id);
		dispatch('actionRun', event.detail);
	}
      let idList = mis_gruposInscripcion.map(obj => obj.grupo.periodo.id);

    const mToggleModalGenerico = () => (mOpenModalGenerico = !mOpenModalGenerico);

    const loadModaGrupos = async (id) => {
        loading.setLoading(true, 'Cargando, espere por favor...');
        const [res, errors] = await apiGET(fetch, 'alumno/idiomas', {
            action: 'loadGrupos',
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
                modalDetalleContent = ModalGrupo;
                mOpenModalGenerico = !mOpenModalGenerico;
                modalTitle = 'INFORMACIÓN DE GRUPOS, CUPOS Y HORARIOS DISPONIBLES';
            }
        }
    };

    function shouldExclude(periodo) {
        return !(idList.includes(periodo.id) || (periodo.idioma.pk === 1 && cursa_modulo_de_ingles === true));
    }

</script>
<!--    <div class="row">-->
<!--        <nav class="bs-stepper mb-5">-->
<!--            <div class="nav nav-tabs bs-stepper-header shadow-sm" id="nav-tab" role="tablist">-->
<!--                {#each idiomas as idioma}-->
<!--                    <button-->
<!--                        class="nav-link active step-trigger"-->
<!--                        id="nav-propu-tab"-->
<!--                        data-bs-toggle="tab"-->
<!--                        data-bs-target="#nav-propu"-->
<!--                        type="button"-->
<!--                        role="tab"-->
<!--                        aria-controls="nav-home"-->
<!--                        aria-selected="true"-->
<!--                >-->
<!--                    <span class="bs-stepper-label">{idioma.display}</span>-->
<!--                </button>-->
<!--                    <div class="bs-stepper-line" />-->
<!--                {/each}-->
<!--            </div>-->
<!--        </nav>-->
<!--    </div>-->
    <div class="row">
        {#each ePeriodo as periodo }
                {#if shouldExclude(periodo)}
                    <div class="col-xxl-3 col-xl-4 col-lg-6 col-12 mb-4">
                        <!-- card -->
                        <div class="card h-100">
                            <!-- card body -->
                            <div class="card-body">
                                <!-- heading-->
                                <div class="d-flex align-items-center
                                justify-content-between">
                                    <!-- text-->
                                    <div>
                                        <h4 class="mb-0"><a href="#" class="text-inherit">{periodo.display}</a></h4>
                                        <span class="text-muted fs-6"></span>
                                    </div>
                                    <!-- dropdown-->

                                </div>
                                <!-- para-->
                                <div class="mt-3 mb-4">
                                    <p class="mb-0"></p>
                                </div>
                                <div class="d-grid gap-2 col-12">
                                    {#if periodo.cronograma_fechas_inscripcion_activa}
                                        <h4 class="fw-bold">¿Deseas inscribirte?</h4>
                                        <button on:click|preventDefault={() => loadModaGrupos(periodo.id)   }
                                                class="btn btn-warning  btn-sm  rounded-pill text-white" type="button">
                                            Consultar grupo disponible
                                        </button>
                                    {:else}
                                        <span class="btn btn-danger">Fechas de inscripción no disponibles.</span>
                                    {/if}
                                </div>
                            </div>
                            <!-- card footer -->
                            <div class="card-footer bg-white p-0">
                                <div class="d-flex justify-content-between ">
                                    <div class="w-50 py-3 px-4 ">
                                        <h6 class="mb-0 text-muted">Fecha inicio de inscripción:</h6>
                                        <p class="text-dark fs-6 fw-semi-bold mb-0">{periodo.fecinicioinscripcion_display}</p>
                                    </div>
                                    <div class="border-start w-50 py-3 px-4">
                                        <h6 class="mb-0 text-muted">Fecha fin de inscripción:</h6>
                                        <p class="text-dark fs-6 fw-semi-bold mb-0">{periodo.fecfininscripcion_display} </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                {/if}
        {:else}
            <h1>No existen cronogramas activos</h1>
        {/each}
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



