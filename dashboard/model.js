class Workflow {
	constructor(steps,nodestypes) {
		this.steps = steps;
		this.nodestypes = nodestypes;
	}

	getOptionById(nodeId) {
		for (var i = 0; i < steps.length; i++) {
			var currentStep = steps[i];
			var childStep = currentStep.getChild();
			if(childStep){
				if(childStep.length){
				for (var j = 0; j < childStep.length; j++) {
					if(childStep[j]){
						if (childStep[j].id == nodeId){
							return childStep[j];
						}

					}
				}
			}

			}
		}
		return null
	}

	getStepByNodeId(nodeId) {
		for (var i = 0; i < steps.length; i++) {
			if (steps[i].id == nodeId){
				return steps[i];
			}
		}
	}

	getFathersStepByNodeId(nodeId) {
		var fathers = [];
		for (var i = 0; i < steps.length; i++) {
			var step = steps[i];

			if(step.getChild()){
				var options = step.getChild();
				if(options.length){

					for (var j = 0; j < options.length; j++) {
						var option = options[j];
						if(option){
							if (option.getNext().id == nodeId){
								fathers.push(steps[i]);
							}
						}
					}

				} else {

					if (step.getChild().id == nodeId){
						fathers.push(steps[i]);
					}
				}
				
			}
			
		}
		return fathers;
	}


	getFatherStepByNodeId(nodeId) {
		
		for (var i = 0; i < steps.length; i++) {
			var step = steps[i];

			if(step.getChild()){
				var options = step.getChild();
				if(options.length){

					for (var j = 0; j < options.length; j++) {
						var option = options[j];
						if(option){
							if (option.getNext().id == nodeId){
								return steps[i];
							}
						}
					}

				} else {

					if (step.getChild().id == nodeId){
						return steps[i];
					}
				}
				
			}
			
		}
		return null;
	}

	addStep(step) {
		this.steps.push(step)
	}

	deleteStep(nodeId) {
		var step = this.getStepByNodeId(nodeId);
		var index = this.steps.indexOf(step);
		if (index > -1) {
			this.steps.splice(index, 1);
		}

	}

	draw(workflowModel) {
		console.log('draw');
	}

	validate() {
		console.log('validate');
	}
}

class NodeType {
	constructor(name,icon,spect) {
		this.name = name;
		this.icon = icon;
		this.spect = spect;
	}
	validate() {
		console.log('validate');
	}
}

class Step {
	constructor(nodeType,id, level) {
		this.nodeType = nodeType;
		this.id = id;
		this.level = level;
	}
	setNodeType(nodeType){
		this.nodeType = nodeType;
	}
	getNodeType(){
		return this.nodeType;
	}
}

class Multiple extends Step {

	addOption(option) {
		if (!this.options){
			this.options = [];
		}
		this.options.push(option,options.length);
	}
	getChild(){
		return this.options;
	}
	canAddChildStep() {
		return true;
	}
	deleteOption(option) {
		var index = this.options.indexOf(step);
		if (index > -1) {
			this.options.splice(index, 1);
		}
	}
	addChildStep(step, text) {
		var option = new Option(text,(Math.floor((Math.random() * 1000) )));
		option.addNext(step);
		this.addOption(option);
	}
	getIdToChild(step) {
		if (this.options){
			for (var i = 0; i < this.options.length; i++) {
				if(this.options[i]){
					if (this.options[i].getNext().id == step.id){
						return this.options[i].id;
					}

				}
			}
		}
	}

	deleteChildStep(clickedStep) {
		for (var i = 0; i < this.options.length; i++) {
			var option = this.options[i];
			if(option){
				if(option.getNext().id == clickedStep.id){
					var index = this.options.indexOf(option);
					if (index > -1) {
						this.options.splice(index, 1);
					}
				}
			}
		}
	}

	getLevelToChild(fatherId) {
		return this.level + 2;
	}
	getEdgesToRender() {
		if (this.options){
			for (var i = 0; i < this.options.length; i++) {
				if(this.options[i]){
					var optionId = this.options[i].id;
					edges.push({from: this.id , to: optionId})
					edges.push({from: optionId , to: this.options[i].getNext().id})
				}
			}
		}
	}
	getNodesToRender(father, level) {
		nodes.push({id: this.id , shape: 'circularImage', image:this.getNodeType().icon, 'level' : level  , label: String(this.id)});
		if (this.options){
			for (var i = 0; i < this.options.length; i++) {
				//Ver que id ponerle
				if(this.options[i]){
					var optionId = this.options[i].id;
					nodes.push({id: optionId, shape: 'circularImage', 'image':'option.png', 'level' : level+1  , label: String("option: " +optionId)});
				}


			}
		}
		
	}
}

class Option {
	constructor(text, id) {
		this.text = text;
		this.id = id;
	}
	deleteNext() {
		this.next = null;
	}
	addNext(step) {
		this.next = step;
	}
	canAddNext() {
		return !this.next;
	}
	getNext(){
		return this.next;
	}
}

class Simple extends Step {
	deleteChildStep() {
		this.next = null;
	}
	canAddChildStep() {
		return !this.next;
	}
	addChildStep(step) {
		this.next = step;
	}
	getChild(){
		return this.next;
	}
	getNext(){
		return this.next;
	}
	getEdgesToRender() {
		if (this.getChild()){
			edges.push({from: this.id , to: this.getChild().id});
		}
		
	}
	getNodesToRender(father, level) {
		nodes.push({id: this.id , shape: 'circularImage','level' : level , image:this.getNodeType().icon, label: String(this.id)});
	}
	getLevelToChild(fatherId) {
		return this.level + 1;
	}
	getIdToChild(step) {
		return this.id;
	}
}