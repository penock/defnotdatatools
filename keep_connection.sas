
* Keep SAS's connection to the server alive, so you can leave the app open. ;
* Press the Stop button when you return to your computer. ;
%macro keep_alive;
    %DO I = 1 %TO 99999;
        DATA _null_;
    /*        do i = 1 to 9999; didn't work, caused some kind of timeouts like at 8min*/
                _null_ = sleep(120, 1);
    /*        end;*/
        RUN;
    %END;
%mend keep_alive;

%keep_alive
