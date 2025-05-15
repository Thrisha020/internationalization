
       IDENTIFICATION DIVISION.
       PROGRAM-ID. COBDDB2.
       DATA DIVISION.
         WORKING-STORAGE SECTION.

         01  WS-SQLREAD           PIC X(1).
      *** IKAN DEMO with DBB with AIBOT Phase *** 
      *** INCLUDING SQLCA COPYBOOK ******
           EXEC SQL
                INCLUDE SQLCA
           END-EXEC.

       PROCEDURE DIVISION.
       MAIN-PARA.

           EXEC SQL
                SELECT IBMREQD INTO: WS-SQLREAD
                FROM SYSIBM.SYSDUMMY1
           END-EXEC.
           Display 'Testing the cobDdb2'.

           STOP RUN.
