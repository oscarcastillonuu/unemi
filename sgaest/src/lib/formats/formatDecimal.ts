export const converToDecimal = (number, decimal = 2) => {
	return Number.parseFloat(number).toFixed(decimal);
}


export const numeric = (elemento, min, max, decimales) => {
	var nvalor;
	const ele = document.getElementById(elemento);
	if (ele) {
		let valor = ele.value;
		if (valor == "") {
			nvalor = parseFloat('0').toFixed(decimales);
			ele.value = nvalor;
		}
		else if (isNaN(valor)) {
			nvalor = parseFloat(min).toFixed(decimales);
			ele.value = nvalor;
		}
		else if (valor < min) {
			nvalor = parseFloat(min).toFixed(decimales);
			ele.value = nvalor;
		}
		else if (max > 0 && valor > max) {
			nvalor = parseFloat(max).toFixed(decimales);
			ele.value = nvalor;
		}
		else {
			nvalor = parseFloat(valor).toFixed(decimales);
			ele.value = nvalor;
		}
	}
	return;
};


