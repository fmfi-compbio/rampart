
import React from 'react';
import Container, {Title} from "./styles";

class MutationsTree extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    createVariantString(variants, level){
        let newText="";
        let first=true;
        for(const variant of variants){
            console.log(variant);
            console.log(variant.name);
            newText+='---'.repeat(level)+"variant: "+ variant.name+" (";
            first=true;
            for(const mutation of variant.mutations){
                if(!first){
                    newText+=", "+mutation.from+mutation.position+mutation.to;
                }
                else{
                    newText+=mutation.from+mutation.position+mutation.to;
                    first=false
                }
            }
            newText+=")\n";
            if(variant.subs.length>0){
                newText+=this.createVariantString(variant.subs, level+1);
            }
        }
        return newText;
    }


    componentDidMount() {
        console.log("props data", this.props.data);
        let newText=this.createVariantString(this.props.data, 0);
        let newLinesToPtagText = newText.split('\n').map(i => {
            return <p>{i}</p>
        });
        this.setState({data:newLinesToPtagText});      
    }

    componentDidUpdate(prevProps) {
        //console.log("prev props", prevProps);
        this.render();
    }


    render() {
        return (
            <Container width="90%" ref="">
                <Title>
                    {"Mutations tree"}
                </Title>
                {this.state.data}
                {this.props.renderProp ? this.props.renderProp : null}
            </Container>
        )
    }
}

export default MutationsTree;