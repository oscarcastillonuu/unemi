<script>
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { create, setOptions } from 'filepond';
	import { registerPlugin } from 'svelte-filepond';
	import FilePondPluginFileValidateType from 'filepond-plugin-file-validate-type';
	export let acceptedFileTypes = ['image/jpeg', 'image/png'];
	export let labelFileTypeNotAllowed = 'Tipo de archivo no permitido';
	export let labelFileTypeNotAllowedMessage = 'Solo se permiten archivos JPEG y PNG';
	export let FileClass = 'pb-0 mb-0';
	export let inputID;
	export let inputName;
	let inputElement;
	let file = null;
	const dispatch = createEventDispatcher();

	onMount(() => {
		// Inicializar FilePond
		registerPlugin(FilePondPluginFileValidateType);
		// console.log(acceptedFileTypes);
		create(inputElement, {
			allowMultiple: true,
			acceptedFileTypes: [...acceptedFileTypes], // Tipos de archivo permitidos
			onaddfile: (error, file) => {
				// console.log('error: ', error);
				// console.log('file: ', file);
				if (error) {
					// Archivo no válido, muestra un mensaje de error
					// alert(error);
				} else {
					file = file;
					dispatch('fileSelected', file);
				}
			},
			onremovefile: () => {
				// Archivo eliminado, dispara el evento personalizado
				file = null;
				dispatch('fileRemoved');
			}
		});

		// Configurar opciones del complemento
		setOptions({
			class: FileClass,
			id: inputID,
			name: inputName,
			plugins: [FilePondPluginFileValidateType],
			//acceptedFileTypes: acceptedFileTypes,
			labelFileTypeNotAllowed: labelFileTypeNotAllowed,
			labelFileTypeNotAllowedMessage: labelFileTypeNotAllowedMessage,
			labelIdle: ['<span class="filepond--label-action">Subir archivo</span>'],
			allowMultiple: false,
			labelInvalidField: 'El campo contiene archivos no válidos',
			style: 'display: none;',
			maxFiles: 1,
			maxParallelUpload: 1
		});
		const divs = document.getElementsByClassName('filepond--credits');

		divs.forEach((element) => {
			element.remove();
		});
		const clss = document.getElementsByClassName('filepond--root');
		if (clss) {
			clss.forEach((element) => {
				element.classList.add('mb-0');
			});
		}
	});
</script>

<input type="file" bind:this={inputElement} />


<style global>
	@import 'filepond/dist/filepond.css';
	.filepond--drop-label {
		border-radius: 0.75rem;
		color: #ffffff;
		background: #335f7f !important;
		box-shadow: 0 0.1875rem 0.625rem rgb(0 0 0 / 15%) !important;
	}
</style>