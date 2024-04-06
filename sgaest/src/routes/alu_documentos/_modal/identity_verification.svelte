<script lang="ts">
	import { onMount } from 'svelte';
	import { Spinner } from 'sveltestrap';

	export let aData;
	let eMatriculaSedeExamen = undefined;
	let load = true;
	const delay = (ms) => new Promise((res) => setTimeout(res, ms));
	onMount(async () => {
		eMatriculaSedeExamen = aData ?? undefined;
		console.log('eMatriculaSedeExamen: ', eMatriculaSedeExamen);
		await delay(2000);
		load = false;
	});
</script>

{#if !load}
	{#if eMatriculaSedeExamen}
		<div class="row m-0 p-0">
			<div class="col-12 m-0 p-0">
				<div class="bg-light rounded-3 ">
					<div class="row align-items-center">
						<div class="col-xl-6 col-12 d-none d-xl-block">
							<div class="text-center">
								<div class="p-10">
									<img src="/assets/images/svg/examen_sede.svg" alt="" class="img-fluid" />
								</div>
							</div>
						</div>
						<div class="col-xl-5 col-12 p-5">
							<div class="">
								<h2 class="display-5 fw-bold pe-lg-12 text-center">Exámenes finales</h2>
								<p class="fs-4 mb-4" style="text-align: justify;">
									<span class="text-primary fw-bold">UNEMI</span> ha implementado el proceso de
									validación de datos, con la finalidad de
									<span class="text-dark fw-semibold">verificar la identidad</span>
									de sus estudiantes durante las diferentes jornadas de
									<span class="text-dark fw-semibold">exámenes finales</span>; para ello, deberás
									completar los siguientes pasos:
								</p>
								<ol class="list-group list-group-numbered">
									<li class="list-group-item d-flex justify-content-between align-items-start">
										<div class="ms-2 me-auto">
											<div class="fw-bold">Paso 1</div>
											Documento de identidad
										</div>
										{#if eMatriculaSedeExamen.tiene_paso_1}
											<span class="text-info fw-bold"><i class="fe fe-check" /></span>
										{:else}
											<span class="text-danger fw-bold"><i class="fe fe-x" /></span>
										{/if}
									</li>
									<li class="list-group-item d-flex justify-content-between align-items-start">
										<div class="ms-2 me-auto">
											<div class="fw-bold">Paso 2</div>
											Foto de perfil
										</div>
										{#if eMatriculaSedeExamen.tiene_paso_2}
											<span class="text-info fw-bold"><i class="fe fe-check" /></span>
										{:else}
											<span class="text-danger fw-bold"><i class="fe fe-x" /></span>
										{/if}
									</li>
								</ol>
							</div>
							<div class="d-grid mt-5 gap-2 d-md-flex justify-content-center">
								<a
									href="/alu_documentos/identity_verification"
									class="btn btn-primary btn-sm rounded-pill"
								>
									{#if eMatriculaSedeExamen.tiene_paso_1}
										Continuar
									{:else}
										Iniciar
									{/if}
								</a>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	{/if}
{:else}
	<div class="row justify-content-center align-items-center p-5 m-0">
		<div class="col-auto text-center">
			<Spinner color="primary" type="border" style="width: 3rem; height: 3rem;" />
			<h3>Verificando la información, espere por favor...</h3>
		</div>
	</div>
{/if}
