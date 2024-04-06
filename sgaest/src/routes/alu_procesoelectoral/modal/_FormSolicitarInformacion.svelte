<script lang="ts">
    import {Label} from "sveltestrap";
    import Select from "svelte-select";
    import {createEventDispatcher, onMount} from "svelte";
    import {loading} from "$lib/store/loadingStore";
    import {apiPOSTFormData} from "$lib/utils/requestUtils";
    import {addToast} from "$lib/store/toastStore";
    import {goto} from "$app/navigation";
    let selected_categoria;
    let categorias = [];
    export let aData;
    let tipo = aData['tipo'];

    tipo.forEach(item => {
        categorias.push({
            value: item['pk'], label: item['display']
        });
    });
    const dispatch = createEventDispatcher();
    onMount(async () => {


	});

    const save = async (formData) => {
		loading.setLoading(true, 'Guardando la información, espere por favor...');
		formData.append('action', 'addsolicitud');
		formData.append('id', aData.id);
		const [res, errors] = await apiPOSTFormData(fetch, 'alumno/procesoelectoral', formData);
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
				loading.setLoading(false, 'Cargando, espere por favor...');
				dispatch('actionRun', { action: 'nextProccess', value: 1 });
			}
		}
	};


    function onSubmit(e) {
		const formData = new FormData(e.target);

		const data: any = {};
		for (let field of formData) {
			const [key, value] = field;
			data[key] = value;
		}
        save(formData);

	}

</script>

<form id="FormInformacion" on:submit|preventDefault={onSubmit}>
<div class="alert alert-info" role="alert" style="text-align: justify; font-size: 12px">
    <b class="alert-heading"><i class="fe fe-help-circle"></i> Recuerda:</b>  Que, en el artículo 4 del Reglamento de Elecciones de la Universidad Estatal de Milagro establece: “El sufragio. - El sufragio es un derecho y un deber del personal académico titular, estudiantes regulares legalmente matriculados a partir del tercer nivel de todas las carreras y modalidades, de los servidores y trabajadores titulares de la institución.”
</div>

    <div id="fieldset_tipo" class="col-lg-12 mb-4" style="float: left; padding-right: 10px;">
        <Label class="control-label pr-2" for="id_tipo"><b>Categoría<span
                style="color:red;margin-left:2px;"><strong>*</strong></span>&nbsp;:</b></Label>

        <Select placeholder="Seleccionar una opción" bind:value={selected_categoria} id="id_tipo"
                name="tipo" items={categorias}></Select>

    </div>

    <div id="fieldset_observacion" class="col-lg-12" style="float: left; padding-right: 10px;">
        <label class="control-label pr-2" for="id_observacion"><b>Observación<span
                style="color:red;margin-left:2px;"><strong>*</strong></span>&nbsp;:</b></label>
        <textarea name="observacion" cols="40" rows="5" class="form-control" col="12" data-nameinput="observacion"
                  required="" id="id_observacion"></textarea>
        <p class="help-text"></p>
    </div>


    <div class="col-12 mb-4">
        <button type="submit" class="btn btn-success form-control">Guardar</button>
    </div>

</form>