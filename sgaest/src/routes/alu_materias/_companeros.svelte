<script lang="ts">
	import { onMount } from 'svelte';
	import { converToAscii, action_print_ireport } from '$lib/helpers/baseHelper';

	export let aData;
	let companeros = [];
	let nombremateria = '';
	onMount(async () => {
		// console.log(aData);
		if (aData.companeros) {
			companeros = aData.companeros;
			nombremateria = aData.nombremateria;
		}
	});

	
	const searchCompa = (e) => {
		//console.log(e);

		const BodyModules = document.querySelectorAll('#mybuscador div #col2');
		for (let i = 0; i < BodyModules.length; i++) {
			const BModule = BodyModules[i];
			const nombre_modules = BModule.querySelector('.nombrescompa');
			if (
				converToAscii(nombre_modules.innerText.toLowerCase()).indexOf(
					converToAscii(e.toLowerCase())
				) === -1
			) {
				BModule.style.display = 'none';
			} else {
				BModule.style.display = '';
			}
		}
	};
</script>

<div style="background-color: #efefef;" class="p-4" id="mybuscador">
	<div class="row">
		<div class="col-12 text-center">
			<h3 class="">{nombremateria}</h3>
		</div>
	</div>
	<input
						class="form-control"
						placeholder="Buscar compañero"
						style="width: 100% !important;"
						on:keyup={({ target: { value } }) => searchCompa(value)}
					/>
	{#if companeros.length > 0}
		<div class="row row-cols-1 row-cols-md-3 g-4 mt-2" >
			{#each companeros as com}
				<div class="col" id = "col2"  >
					<div class="card h-100" >
						<div class="card-body" >
							<div class="text-center">
								{#if com.matricula.inscripcion.persona.foto_perfil}
									<img
										onerror="this.onerror=null;this.src='./image.png'"
										src={com.matricula.inscripcion.persona.foto_perfil}
										class="rounded-circle avatar-xl mb-3"
										alt=""
									/>
								{:else}
									<img
										onerror="this.onerror=null;this.src='./image.png'"
										src="./images/iconos/profesor_small.png"
										class="rounded-circle avatar-xl mb-3"
										alt=""
									/>
								{/if}

								<h4 class="mb-1 nombrescompa">
									{com.matricula.inscripcion.persona.apellido1}
									{com.matricula.inscripcion.persona.apellido2}
									{com.matricula.inscripcion.persona.nombres}
								</h4>
							
							</div>
							<div class="d-flex justify-content-between border-bottom py-2 mt-4 fs-6">
								<span><strong> Carrera: </strong> {com.matricula.inscripcion.carrera.nombre} </span>
							</div>
							
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>

