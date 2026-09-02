



document.addEventListener('DOMContentLoaded', () => {
    const paymentSelectElement = document.getElementById('paymentType');
    const amountInputElement = document.getElementById("amountInput");
    const paymentNote = document.getElementById("paymentNote");


    const properties = document.getElementById("properties");
    const fromNumber = document.getElementById("fromNumber");
    const payYear = document.getElementById("payYear");
    const payMonth = document.getElementById("payMonth");
    const pinRef = document.getElementById("pinRef");
    const cashier = document.getElementById("cashier");

    const myColUser = document.getElementById("myColUser");
    const myColAmount = document.getElementById("myColAmount");
    
    if (paymentSelectElement) {
        paymentSelectElement.addEventListener('change', (e) => {
            if (e.target.value == 'Savings'){
                amountInputElement.value = 5000;
                paymentNote.value = "This is my monthly fee please kindly check and approve my transaction.";

                properties.style.display = "none";

                cashier.style.display = 'block';
                fromNumber.style.display = 'block';
                payYear.style.display = 'block';
                payMonth.style.display = 'block';
                pinRef.style.display = 'block';

                myColUser.classList.remove('col-md-12', 'mb-12');
                myColAmount.classList.remove('col-md-12', 'mb-12');

                myColUser.classList.add('col-md-6', 'mb-6');
                myColAmount.classList.add('col-md-6', 'mb-6');

            }
            else if (e.target.value == 'Expense'){
                amountInputElement.value = 0.00;
                paymentNote.value = "I have expense this amount to development unity-power assosiation.";

                properties.style.display = "none";

                cashier.style.display = 'block';
                fromNumber.style.display = 'block';
                payYear.style.display = 'block';
                payMonth.style.display = 'block';
                pinRef.style.display = 'block';

                myColUser.classList.remove('col-md-12', 'mb-12');
                myColAmount.classList.remove('col-md-12', 'mb-12');

                myColUser.classList.add('col-md-6', 'mb-6');
                myColAmount.classList.add('col-md-6', 'mb-6');
            }
            else if (e.target.value == 'Loan'){
                amountInputElement.value = 0.00;
                paymentNote.value = "Unity-Power take this amount as Loan for our Welfare.";

                properties.style.display = "none";

                cashier.style.display = 'block';
                fromNumber.style.display = 'block';
                payYear.style.display = 'block';
                payMonth.style.display = 'block';
                pinRef.style.display = 'block';

                myColUser.classList.remove('col-md-12', 'mb-12');
                myColAmount.classList.remove('col-md-12', 'mb-12');

                myColUser.classList.add('col-md-6', 'mb-6');
                myColAmount.classList.add('col-md-6', 'mb-6');
            }
            else if (e.target.value == 'Welfare'){
                properties.style.display = "block";
                paymentNote.value = "Unity-Power pay this amount to buy land space kindly verify this transaction.";

                cashier.style.display = 'none';
                fromNumber.style.display = 'none';
                payYear.style.display = 'none';
                payMonth.style.display = 'none';
                pinRef.style.display = 'none';

                myColUser.classList.remove('col-md-6', 'mb-6');
                myColAmount.classList.remove('col-md-6', 'mb-6');

                myColUser.classList.add('col-md-12', 'mb-12');
                myColAmount.classList.add('col-md-12', 'mb-12');
            }
        });
    } else {
        console.error("Could not find element with id 'pymentType'");
    }
});


